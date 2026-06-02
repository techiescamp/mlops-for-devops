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
    query = request.query
    print(query)

    # Step 1: Retrieve — embed query + search S3 Vectors
    try:
        results, _ = retrieve(bedrock, s3_vectors, BEDROCK_EMBED_MODEL, INDEX_ARN, query)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Retrieval error: {str(e)}")

    context     = "\n\n".join(doc["content"] for doc in results)
    source_list = [doc.get("metadata", {}).get("source") for doc in results]

    # Step 2: Build messages with chat history from memory
    messages = get_chat_history(memory, query)
    messages.append({"role": "user", "content": [{'text': f"Context: {context}\nQuestion: {query}"}]})

    # Step 3: Generate — call Bedrock LLM
    output = generate(bedrock, BEDROCK_LLM_MODEL, messages, SYSTEM_PROMPT)

    # Step 4: Save to memory
    save_to_memory(memory, query, output)

    return {"answer": output, "source": source_list}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)