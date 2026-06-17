import os
import sys
import uvicorn
import boto3
from botocore.config import Config
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Add each pipeline step directory to Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'retrieval'))
sys.path.insert(0, os.path.join(BASE_DIR, 'generation'))
sys.path.insert(0, os.path.join(BASE_DIR, 'memory'))

from retriever import retrieve
from generator import generate
from memory import create_memory, get_chat_history, save_to_memory

# Add monitoring paths
sys.path.insert(0, os.path.join(BASE_DIR, '../../rag-monitoring'))
from cloudwatch_client import push_metric
from retrieval_metrics import compute_similarity_and_precision_like, compute_recall_like, compute_hit
from generation_metrics import (evaluate_faithfulness, compute_hallucination_rate,
                                evaluate_answer_relevance, compute_cost,
                                compute_context_utilization, detect_refusal)

load_dotenv(os.path.join(BASE_DIR, '../.env'))

# env
BEDROCK_LLM_MODEL    = os.environ["BEDROCK_LLM_MODEL"]
BEDROCK_EMBED_MODEL  = os.environ["BEDROCK_EMBEDDING_MODEL_ID"]
AWS_REGION           = os.environ["AWS_REGION"]
AWS_ACCOUNT_ID       = os.environ["AWS_ACCOUNT_ID"]
S3_VECTOR_BUCKET     = os.environ["S3_VECTOR_BUCKET_NAME"]
S3_VECTOR_INDEX      = os.environ["S3_VECTOR_INDEX_NAME"]
HOST                 = os.environ["MAIN_BACKEND_HOST"]
PORT                 = int(os.environ["MAIN_BACKEND_PORT"])

INDEX_ARN = f"arn:aws:s3vectors:{AWS_REGION}:{AWS_ACCOUNT_ID}:bucket/{S3_VECTOR_BUCKET}/index/{S3_VECTOR_INDEX}"

# AWS clients
aws_config = Config(connect_timeout=10, read_timeout=60, retries={'max_attempts': 3})
bedrock   = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=aws_config)
s3_vectors = boto3.client("s3vectors",      region_name=AWS_REGION, config=aws_config)

# Conversation memory (in-process, resets on restart)
memory = create_memory()

SYSTEM_PROMPT = """
    You are a helpful AI assistant that explains concepts to beginners with examples and code.
    If the context does NOT help answer the question, clearly mention that it's "out of context"
"""

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str
    isEvaluate: bool = True


@app.post("/query")
async def query_rag(request: QueryRequest):
    import time
    end_to_end_start = time.time()
    query = request.query
    print(query)

    # Step 1: Retrieve — embed query + search S3 Vectors
    retrieval_start = time.time()
    try:
        results, _, raw_vectors = retrieve(bedrock, s3_vectors, BEDROCK_EMBED_MODEL, INDEX_ARN, query)
        retrieval_latency = time.time() - retrieval_start
        push_metric("RetrievalLatency", retrieval_latency, "Seconds", namespace="RAG/Retrieval")
        push_metric("QueryLatency", retrieval_latency, "Seconds", namespace="RAG/VectorDB")
        push_metric("IndexHealthStatus", 1, "None", namespace="RAG/VectorDB")
    except Exception as e:
        push_metric("RetrievalFailures", 1, "Count", namespace="RAG/Retrieval")
        push_metric("QueryFailures", 1, "Count", namespace="RAG/VectorDB")
        push_metric("IndexHealthStatus", 0, "None", namespace="RAG/VectorDB")
        raise HTTPException(status_code=502, detail=f"Retrieval error: {str(e)}")

    context     = "\n\n".join(doc["content"] for doc in results if doc.get("content"))
    source_list = [doc.get("metadata", {}).get("source") for doc in results]

    # Push retrieval metrics calculations
    num_docs = len(results)
    push_metric("RetrievedDocsCount", num_docs, "Count", namespace="RAG/Retrieval")
    push_metric("HitRate", compute_hit(num_docs), "None", namespace="RAG/Retrieval")

    # AvgSimilarity, PrecisionProxy, RecallProxy
    avg_sim, precision_like = compute_similarity_and_precision_like(results, metric='COSINE', top_weighted=True)
    push_metric('AvgSimilarity', avg_sim, 'None', namespace="RAG/VectorDB")
    push_metric('PrecisionProxy', precision_like, 'None', namespace="RAG/VectorDB")

    recall_like = compute_recall_like(vectors=raw_vectors)
    push_metric('RecallProxy', recall_like, 'None', namespace="RAG/VectorDB")

    # Step 2: Build messages with chat history from memory
    messages = get_chat_history(memory, query)
    messages.append({"role": "user", "content": [{'text': f"Context: {context}\nQuestion: {query}"}]})

    # Step 3: Generate — call Bedrock LLM
    generation_start_time = time.time()
    try:
        output, response = generate(bedrock, BEDROCK_LLM_MODEL, messages, SYSTEM_PROMPT)
        llm_latency = time.time() - generation_start_time
        push_metric('LLMLatency', llm_latency, 'Seconds', namespace="RAG/Generation")
        
        # Word counts
        response_length = len(output.split())
        push_metric('ResponseLength', response_length, 'Count', namespace="RAG/Generation")

        # Hallucination rate
        hallucination_ratio = compute_hallucination_rate(output, context)
        push_metric('HallucinationRate', hallucination_ratio, 'None', namespace="RAG/Generation")

        # Token Usage
        usage_data = response.get('usage', {})
        if usage_data:
            input_tokens  = usage_data.get('inputTokens', 0)
            output_tokens = usage_data.get('outputTokens', 0)
            push_metric("LLMInputTokens",  input_tokens,                    'Count', namespace="RAG/Generation")
            push_metric("LLMOutputTokens", output_tokens,                   'Count', namespace="RAG/Generation")
            push_metric("LLMTotalTokens",  usage_data.get('totalTokens', 0),'Count', namespace="RAG/Generation")
            cost = compute_cost(input_tokens, output_tokens)
            if cost is not None:
                push_metric("CostPerQuery", cost, "None", namespace="RAG/Generation")

        # Bedrock internal latency
        metrics_data = response.get('metrics', {})
        if metrics_data:
            push_metric("LLMLatencyBedrock", metrics_data.get('latencyMs', 0), 'Milliseconds', namespace="RAG/Generation")

        # Faithfulness Grade
        score = evaluate_faithfulness(bedrock, BEDROCK_LLM_MODEL, context, output)
        if score is not None:
            push_metric("FaithfulnessScore", score, "None", namespace="RAG/Generation")

        # Answer Relevance
        relevance = evaluate_answer_relevance(bedrock, BEDROCK_LLM_MODEL, query, output)
        if relevance is not None:
            push_metric("AnswerRelevance", relevance, "None", namespace="RAG/Generation")

        # Context Utilization
        utilization = compute_context_utilization(output, context)
        push_metric("ContextUtilization", utilization, "None", namespace="RAG/Generation")

        # Refusal Detection
        push_metric("RefusalRate", detect_refusal(output), "None", namespace="RAG/Generation")

    except Exception as e:
        print(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

    # Step 4: Save to memory
    save_to_memory(memory, query, output)

    # End-to-end performance
    end_to_end_latency = time.time() - end_to_end_start
    push_metric("EndToEndLatency", end_to_end_latency, "Seconds", namespace="RAG/Generation")

    return {"answer": output, "source": source_list}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)