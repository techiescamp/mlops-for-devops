import json
import numpy as np
import boto3
from botocore.config import Config
from typing import List


def create_clients(aws_region):
    config = Config(read_timeout=60, connect_timeout=10, retries={"max_attempts": 3})
    bedrock_rt = boto3.client("bedrock-runtime", region_name=aws_region, config=config)
    s3_vectors  = boto3.client("s3vectors",       region_name=aws_region, config=config)
    return bedrock_rt, s3_vectors


def as_float32_vec(vec: List[float]) -> List[float]:
    return np.asarray(vec, dtype=np.float32).tolist()


def embed_query(bedrock_rt, model_id: str, query: str):
    response = bedrock_rt.invoke_model(
        modelId=model_id,
        body=json.dumps({"inputText": query}),
        contentType="application/json"
    )
    body = json.loads(response['body'].read())
    return body['embedding'], body.get("inputTextTokenCount", 0)


def search_vectors(s3_vectors_client, index_arn: str, query_vector: List[float], top_k: int = 5):
    response = s3_vectors_client.query_vectors(
        indexArn=index_arn,
        topK=top_k,
        queryVector={"float32": as_float32_vec(query_vector)},
        filter=None,
        returnMetadata=True,
        returnDistance=True
    )
    return [{
        "key":      doc.get("key"),
        "score":    float(doc.get("distance")) if doc.get("distance") is not None else None,
        "content":  doc.get("metadata", {}).get("content"),
        "metadata": doc.get("metadata")
    } for doc in response.get("vectors", [])]


def retrieve(bedrock_rt, s3_vectors_client, embedding_model_id: str, index_arn: str, query: str, top_k: int = 5):
    embedding, token_count = embed_query(bedrock_rt, embedding_model_id, query)
    results = search_vectors(s3_vectors_client, index_arn, embedding, top_k)
    return results, token_count
