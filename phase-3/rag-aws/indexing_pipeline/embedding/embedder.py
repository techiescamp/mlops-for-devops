import json
import boto3
from botocore.config import Config
from typing import List
from langchain_core.documents import Document


def create_bedrock_client(aws_region):
    config = Config(
        read_timeout=60,
        connect_timeout=10,
        retries={"max_attempts": 3}
    )
    return boto3.client("bedrock-runtime", region_name=aws_region, config=config)


def embed_documents(bedrock_rt, model_id, contents, token_count):
    embed_docs = []
    for text in contents:
        response = bedrock_rt.invoke_model(
            modelId=model_id,
            contentType="application/json",
            accept="application/json",
            body=json.dumps({"inputText": text})
        )
        result = json.loads(response.get("body").read())
        embed = result.get("embedding")
        if not embed:
            raise RuntimeError(f"Embedding not found in Bedrock response: {result}")
        embed_docs.append(embed)
        token_count += result.get("inputTextTokenCount", 0)
        print('token-count: ', token_count)
    return embed_docs, token_count


def process_batch(bedrock_rt, model_id, batch_documents: List[Document], token_count: int):
    contents = [doc.page_content for doc in batch_documents]
    if not contents:
        return [], token_count

    print(f"No.of Contents: {len(contents)}")
    embeddings, token_count = embed_documents(bedrock_rt, model_id, contents, token_count)

    payload = []
    for doc, emb in zip(batch_documents, embeddings):
        payload.append({
            "embeddings": emb,
            "content": doc.page_content,
            "metadata": doc.metadata
        })
    return payload, token_count
