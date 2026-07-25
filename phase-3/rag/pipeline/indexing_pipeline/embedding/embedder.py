import json
import time
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError
from typing import List
from langchain_core.documents import Document

EMBED_MAX_RETRIES = 3
EMBED_RETRY_DELAY = 5


def create_bedrock_client(aws_region):
    config = Config(
        read_timeout=60,
        connect_timeout=10,
        retries={"max_attempts": 3}
    )
    return boto3.client("bedrock-runtime", region_name=aws_region, config=config)


def embed_text(bedrock_rt, model_id, text):
    """Invoke the embedding model for a single chunk, retrying on transient
    Bedrock errors (e.g. ModelErrorException) before giving up on this chunk."""
    last_error = None
    for attempt in range(1, EMBED_MAX_RETRIES + 1):
        try:
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
            return embed, result.get("inputTextTokenCount", 0)
        except ClientError as e:
            last_error = e
            error_code = e.response.get("Error", {}).get("Code", "")
            print(f"⚠️ Bedrock error on attempt {attempt}/{EMBED_MAX_RETRIES} ({error_code}): {e}")
            if attempt < EMBED_MAX_RETRIES:
                time.sleep(EMBED_RETRY_DELAY * attempt)

    print(f"❌ Skipping chunk after {EMBED_MAX_RETRIES} failed attempts: {last_error}")
    return None, 0


def embed_documents(bedrock_rt, model_id, contents, token_count):
    embed_docs = []
    for text in contents:
        embed, tokens = embed_text(bedrock_rt, model_id, text)
        embed_docs.append(embed)
        token_count += tokens
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
        if emb is None:
            continue
        payload.append({
            "embeddings": emb,
            "content": doc.page_content,
            "metadata": doc.metadata
        })
    return payload, token_count
