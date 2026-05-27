import os
import sys
import time
from dotenv import load_dotenv
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Add each pipeline step directory to Python path so modules can be imported by name
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'ingestion'))
sys.path.insert(0, os.path.join(BASE_DIR, 'chunking'))
sys.path.insert(0, os.path.join(BASE_DIR, 'embedding'))
sys.path.insert(0, os.path.join(BASE_DIR, 'vector_store'))

from helper_functions import clone_or_pull_repo, copy_docs, get_hash_file, load_existing_hashes, load_md_files, save_hashes
from chunker import chunk_documents
from embedder import create_bedrock_client, process_batch
from vector_store import create_s3_vectors_client, store_vectors

load_dotenv(os.path.join(BASE_DIR, '../.env'))

# env
AWS_REGION           = os.environ["AWS_REGION"]
AWS_ACCOUNT_ID       = os.environ["AWS_ACCOUNT_ID"]
EMBEDDING_MODEL_ID   = os.environ["BEDROCK_EMBEDDING_MODEL_ID"]
REPO_URL             = os.environ["K8_REPO_URL"]
S3_VECTOR_BUCKET     = os.environ["S3_VECTOR_BUCKET_NAME"]
S3_VECTOR_INDEX      = os.environ["S3_VECTOR_INDEX_NAME"]

INDEX_ARN = f"arn:aws:s3vectors:{AWS_REGION}:{AWS_ACCOUNT_ID}:bucket/{S3_VECTOR_BUCKET}/index/{S3_VECTOR_INDEX}"

# Batch config
EMBEDDING_BATCH_SIZE = 50
STORE_BATCH_SIZE     = 50
BATCH_DELAY          = 1
RATE_LIMIT_DELAY     = 60

# AWS clients
bedrock_rt = create_bedrock_client(AWS_REGION)
s3_vectors = create_s3_vectors_client(AWS_REGION)


def run_pipeline():
    print("🚀 Starting indexing pipeline...")

    # Step 1: Ingestion — clone/pull repo and copy markdown docs
    print("\n1️⃣  Step-1: Ingestion")
    clone_or_pull_repo(REPO_URL)
    copy_docs()

    # Step 2: Load files + hash check to skip unchanged docs
    print("\n2️⃣  Step-2: Load & detect changes")
    existing_hashes = load_existing_hashes()
    new_hashes = {}
    to_embed = []

    md_files = load_md_files()
    for doc in md_files:
        filepath = doc["filepath"]
        content_hash = get_hash_file(doc["content"])
        new_hashes[filepath] = content_hash
        if existing_hashes.get(filepath) != content_hash:
            print(f"📌 Change detected: {filepath}")
            to_embed.append(doc)
        else:
            print(f"✅ No change: {filepath}")

    if not to_embed:
        print("🎉 All documents are up-to-date. Nothing to embed.")
        return
    save_hashes(new_hashes)

    # Step 3: Chunking — split docs into 1500-token chunks
    print("\n3️⃣  Step-3: Chunking")
    chunks = chunk_documents(to_embed)

    # Step 4: Embedding + storing into S3 Vectors
    print("\n4️⃣  Step-4: Embedding & storing vectors")
    total_processed = 0
    successful_batches = 0
    token_count = 0

    for i in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[i:i + EMBEDDING_BATCH_SIZE]
        batch_num = i // EMBEDDING_BATCH_SIZE + 1
        total_batches = (len(chunks) + EMBEDDING_BATCH_SIZE - 1) // EMBEDDING_BATCH_SIZE
        print(f"\nProcessing batch {batch_num}/{total_batches}")

        payload_items, token_count = process_batch(bedrock_rt, EMBEDDING_MODEL_ID, batch, token_count)
        if not payload_items:
            print("Skipping empty batch...")
            continue
        total_processed += len(payload_items)

        for j in range(0, len(payload_items), STORE_BATCH_SIZE):
            store_batch = payload_items[j:j + STORE_BATCH_SIZE]
            try:
                result = store_vectors(s3_vectors, INDEX_ARN, store_batch)
                successful_batches += 1
                print(f"✅ Stored batch {successful_batches}: {result}")
                time.sleep(BATCH_DELAY)
            except Exception as e:
                print(f"❌ Failed to store batch: {e}")
                time.sleep(RATE_LIMIT_DELAY)
                try:
                    result = store_vectors(s3_vectors, INDEX_ARN, store_batch)
                    successful_batches += 1
                    print(f"✅ Stored batch {successful_batches} on retry")
                except Exception as retry_e:
                    print(f"❌ Retry also failed: {retry_e}")

    print(f"\n✅ Indexing complete — documents: {total_processed}, batches: {successful_batches}")


if __name__ == "__main__":
    try:
        run_pipeline()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise