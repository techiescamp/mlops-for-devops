import uvicorn
import os
import json
import time
import datetime
import numpy as np

import boto3
from botocore.config import Config

from typing import List, Dict, Any, override
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# env constants
AWS_REGION = os.environ["AWS_REGION"]
AWS_ACCOUNT_ID = os.environ["AWS_ACCOUNT_ID"]
BEDROCK_EMBEDDING_MODEL_ID = os.environ["BEDROCK_EMBEDDING_MODEL_ID"]

S3_VECTOR_BUCKET = os.environ["S3_VECTOR_BUCKET_NAME"]         # name of your S3 vector bucket
S3_VECTOR_INDEX = os.environ["S3_VECTOR_INDEX_NAME"]          # index name inside the vector bucket

PUT_VECTORS_BATCH_SIZE = 100
TOKEN_LOG_FILE = "query_log.json"
HOST = os.environ["VECTOR_DB_HOST"]
PORT = int(os.environ["VECTOR_DB_PORT"])

# aws configuration
config = Config(
    read_timeout=60,
    connect_timeout=10,
    retries={"max_attempts": 3}
)
bedrock_rt = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=config)
s3_vectors = boto3.client("s3vectors", region_name=AWS_REGION, config=config)


# Fast API Setup
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schema
class EmbeddingItem(BaseModel):
    embeddings: List[float]
    content: str
    metadata: Dict[str, Any]


class QueryRequest(BaseModel):
    query: str

# helpers
def as_float32_vec(vec: List[float]) -> List[float]:
    """ Ensure vector is float32 (s3 requires vectors in float32) """
    arr = np.asarray(vec, dtype=np.float32)
    return arr.tolist()


def chunk_list(lst: List[Any], size: int):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def bedrock_llm(query: str) -> List[float]:
    """Generate embedding using Bedrock"""
    try:
        body = json.dumps({"inputText": query})
        response = bedrock_rt.invoke_model(
            modelId=BEDROCK_EMBEDDING_MODEL_ID,
            body=body,
            contentType="application/json"
        )
        response_body = json.loads(response['body'].read())
        embedding = response_body['embedding']
        token = response_body["inputTextTokenCount"]
        return embedding, token
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Embedding generation failed: {str(e)}")


        
def log_token_count(query, token_count):
    if os.path.exists(TOKEN_LOG_FILE):
        with open(TOKEN_LOG_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = []
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "query": query,
        "tokens_used": token_count
    }
    data.append(entry)
    with open(TOKEN_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("🎉 Token Count logged")



# api endpoints
@app.post("/store")
def store_embeddings(items: List[EmbeddingItem]):
    """
        Accepts list of items:
        { "embeddings": [...], "content": "...", "metadata": {...} }
        and writes them to the configured S3 Vector index using PutVectors.
        - We include `content` inside the vector `metadata` so the data is returned on queries (or store it elsewhere if you prefer).
    """
    print(f"Recieved {len(items)} for storing vectors")
    print(items)
    # ex: [ 
    # {'embeddings': [23, 24,...], 'content': "hello world 123", 'metadata': {'source': 'hello-0'}},
    # {'embeddings': [23, 24,...], 'content': "hello world 123", 'metadata': {'source': 'hello-0'}},
    # .......
    # ... 20 items
    # ]
    if not items:
        return { "status": "error", "stored": 0 }
    
    vectors_payload = []
    for idx, item in enumerate(items):
        # unique key for vector
        # if id exists in metadata use that
        # else create new key with time
        key = item.metadata.get("id") or f"doc-{int(time.time()*1000)}-{idx}"

        # add content to metadata for validation to s3 vector
        metadata_with_content = dict(item.metadata)
        metadata_with_content["content"] = item.content

        vectors_payload.append({
            "key": key,
            "data": {"float32": as_float32_vec(item.embeddings)},
            "metadata": metadata_with_content
        })
        # ex: same as 20 items woth s3 vector format

    # now store embeddings in batches
    stored = 0
    try:
        for batch in chunk_list(vectors_payload, PUT_VECTORS_BATCH_SIZE):
            s3_vectors.put_vectors(
                indexArn=f"arn:aws:s3vectors:{AWS_REGION}:{AWS_ACCOUNT_ID}:bucket/{S3_VECTOR_BUCKET}/index/{S3_VECTOR_INDEX}",
                vectors=batch
            )
            stored += len(batch)
        return {"status": "success", "stored": stored}
    except s3_vectors.exceptions.TooManyRequestsException as e:
        raise HTTPException(status_code=429, detail=f"Rate limited by S3 Vectors: {str(e)}")
    except Exception as e:
        print(e)
        # raise HTTPException(status_code=500, detail=str(e))
    


@app.post("/search")
async def search_query(request: QueryRequest):
    """
        Receive a textual query, embed via Bedrock, then query the S3 Vectors index.
        Returns list of nearest neighbors with distances and metadata (including content).
    """
    query = request.query
    query_embed, query_token = bedrock_llm(query)
    log_token_count(query, query_token)
    query_vec_f32 = as_float32_vec(query_embed)
    
    try: 
        top_k: int = 5
        response = s3_vectors.query_vectors(
            indexArn=f"arn:aws:s3vectors:{AWS_REGION}:{AWS_ACCOUNT_ID}:bucket/{S3_VECTOR_BUCKET}/index/{S3_VECTOR_INDEX}",
            topK=top_k,
            queryVector={"float32": query_vec_f32},
            filter=None,
            returnMetadata=True,
            returnDistance=True
        )
        # {
        #     'vectors': [
        #         {
        #             'key': 'string',
        #             'data': {
        #                 'float32': [
        #                     ...,
        #                 ]
        #             },
        #             'metadata': {...}|[...]|123|123.4|'string'|True|None,
        #             'distance': ...
        #         },
        #         ... 
        #         ... top_k
        #     ]
        # }
        vectors = response.get("vectors", [])
        payload = [{
                "key": doc.get("key"),
                "score": float(doc.get("distance")) if doc.get("distance") is not None else None,
                "content": doc.get("metadata", {}).get("content"), 
                "metadata": doc.get("metadata")
            }
            for doc in vectors
        ]
        print("Sent result to main-backend")
        return payload
        
    except s3_vectors.exceptions.AccessDeniedException as e:
        # Missing s3vectors:GetVectors or s3vectors:QueryVectors or related permissions
        raise HTTPException(status_code=403, detail=f"Access denied: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ---------- Health ----------
@app.get("/health")
async def health_check():
    return {"status": "healthy"}



# ---------- If run directly ----------
if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT, reload=False)



