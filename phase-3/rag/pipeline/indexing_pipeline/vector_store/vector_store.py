import time
import numpy as np
import boto3
from botocore.config import Config
from typing import List, Any


def create_s3_vectors_client(aws_region):
    config = Config(
        read_timeout=60,
        connect_timeout=10,
        retries={"max_attempts": 3}
    )
    return boto3.client("s3vectors", region_name=aws_region, config=config)


def as_float32_vec(vec: List[float]) -> List[float]:
    return np.asarray(vec, dtype=np.float32).tolist()


def chunk_list(lst: List[Any], size: int):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


# S3 Vectors rejects a whole put_vectors call if any single record's
# filterable metadata exceeds this limit, so a single oversized chunk can
# drop an entire batch of otherwise-valid vectors.
MAX_METADATA_BYTES = 2048
METADATA_HEADROOM_BYTES = 200  # room for the other metadata keys stored alongside content


def _truncate_to_byte_limit(text: str, max_bytes: int) -> str:
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    return encoded[:max_bytes].decode("utf-8", errors="ignore")


def store_vectors(s3_vectors_client, index_arn: str, items: list, batch_size: int = 100):
    if not items:
        return {"status": "error", "stored": 0}

    vectors_payload = []
    for idx, item in enumerate(items):
        key = item.get("metadata", {}).get("id") or f"doc-{int(time.time()*1000)}-{idx}"
        metadata_with_content = dict(item["metadata"])
        metadata_with_content["content"] = _truncate_to_byte_limit(
            item["content"], MAX_METADATA_BYTES - METADATA_HEADROOM_BYTES
        )
        vectors_payload.append({
            "key": key,
            "data": {"float32": as_float32_vec(item["embeddings"])},
            "metadata": metadata_with_content
        })

    stored = 0
    for batch in chunk_list(vectors_payload, batch_size):
        s3_vectors_client.put_vectors(indexArn=index_arn, vectors=batch)
        stored += len(batch)
    return {"status": "success", "stored": stored}
