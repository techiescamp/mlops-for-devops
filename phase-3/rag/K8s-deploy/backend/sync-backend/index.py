import datetime
import os
import requests
import time
import json
import boto3
from botocore.config import Config
from typing import List
from dotenv import load_dotenv

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from helper_functions import clone_or_pull_repo, copy_docs, get_hash_file, load_existing_hashes, load_md_files, save_hashes, log_token_count


# 
load_dotenv()

# env constants
AWS_REGION = os.environ["AWS_REGION"]
BEDROCK_EMBEDDING_MODEL_ID = os.environ["BEDROCK_EMBEDDING_MODEL_ID"]

print(os.environ["K8_REPO_URL"])

REPO_URL = os.environ["K8_REPO_URL"]
VECTOR_DB_URL = os.environ["VECTOR_DB_URL"]
HOST = os.environ.get("HOST", "0.0.0.0")
PORT = int(os.environ.get("PORT", "8002")) 


# Batch configuration
EMBEDDING_BATCH_SIZE = 50  # Reduced batch size for embeddings
STORE_BATCH_SIZE = 50      # Batch size for vector store uploads
BATCH_DELAY = 1             # Delay between batches in seconds
RATE_LIMIT_DELAY = 60       # Delay when hitting rate limits in seconds


# aws configuration
config = Config(
    read_timeout=60,
    connect_timeout=10,
    retries={"max_attempts": 3}
)
bedrock_rt = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=config)

# retry strategy
retry_strategy = Retry(
    total=3,  # number of retries
    backoff_factor=1,  # wait 1, 2, 4, 8, 16 seconds between retries
    status_forcelist=[429, 500, 502, 503, 504]  # HTTP status codes to retry on
)
http_adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", http_adapter)
session.mount("https://", http_adapter)


def call_text_splitter(md_docs):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=50)
    documents = []

    try:
        for doc in md_docs:
            split_texts = text_splitter.split_text(doc['content'])
            for i, chunk in enumerate(split_texts):
                document = Document(
                    page_content=chunk,
                    metadata={
                        'source': f"{doc['filename']}-{i}" 
                    }
                )
                documents.append(document)
        print(f"Total document chunks created: {len(documents)}")
        # Total document chunks created: 1554
        
        # Safely print first document details if available
        if documents:
            first_doc = documents[0] 
            print(f"First chunk sample - Content length: {len(first_doc.page_content)}")
            print(f"First chunk sample - Metadata: {first_doc.metadata}")
        else:
            print(f"Warning: Could not print first document details: {e}")
        return documents

    except Exception as e:
        print(f"Error in text splitting: {e}")
        raise



def embed_documents(contents, token_count):
    embed_docs = []
    for text in contents:
        body = {"inputText": text}
        response = bedrock_rt.invoke_model(
            modelId=BEDROCK_EMBEDDING_MODEL_ID,
            contentType="application/json",
            accept="application/json",
            body=json.dumps(body)
        )
        result = json.loads(response.get("body").read())
        
        embed = result.get("embedding")
        if not embed:
            raise RuntimeError(f"Embedding not found in Bedrock response: {embed}")
        
        embed_docs.append(embed)
        # call token count function
        token_count += result.get("inputTextTokenCount", 0)
        print('token-count: ', token_count)
    return embed_docs, token_count


# process documents in batches
def process_batch(batch_documents: List[Document], token_count: int):
    """Process a batch of documents."""
    contents = [doc.page_content for doc in batch_documents]
    if not contents:
        return []

    print(f"No.of Contents: {len(contents)}")
    embeddings, token_count = embed_documents(contents, token_count)
    payload = []
    for doc, emb in zip(batch_documents, embeddings):
        payload.append({
            "embeddings": emb,
            "content": doc.page_content,
            "metadata": doc.metadata
        })
    return payload, token_count


def store_embeddings(payload_batch):
    try:
        response = session.post(f"{VECTOR_DB_URL}/store", json=payload_batch)
        response.raise_for_status()
        return True
    except Exception as e:
        print(f"Error storing embeddings batch: {e}")
        if "429" in str(e):
            print(f"Rate limit hit, waiting {RATE_LIMIT_DELAY} seconds...")
            time.sleep(RATE_LIMIT_DELAY)
        return False


def rerun_embeddings():
    print("🔁 Computing text embeddings for filenames...")

    # intialize hash
    existing_hashes = load_existing_hashes()
    new_hashes = {}
    to_embed = []

    # document loading process
    print("1️⃣ Step-1: Loading markdown files...")
    md_files = load_md_files()
    if md_files:
        print(f".md-files sample: {md_files[0]}")

    print("2️⃣ Step-2: Detect hashes to avoid re-embeddings...")
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
        print("🎉 All documents are up-to-date.")
        return
    save_hashes(new_hashes)
    
    # Text Splitting Process
    print("3️⃣ Step-3: Text splitting process...")
    chunk_documents = call_text_splitter(to_embed)

    # Process documents in batches
    total_processed = 0
    successful_batches = 0
    token_count = 0

    for i in range(0, len(chunk_documents), EMBEDDING_BATCH_SIZE):
        batch = chunk_documents[i:i + EMBEDDING_BATCH_SIZE]
        print(f"\nProcessing batch {i//EMBEDDING_BATCH_SIZE + 1}/{(len(chunk_documents) + EMBEDDING_BATCH_SIZE - 1)//EMBEDDING_BATCH_SIZE}")

        payload_items, token_count = process_batch(batch, token_count)

        if not payload_items:
            print("Skipping empty batch...")
            continue
        total_processed += len(payload_items)

        for j in range(0, len(payload_items), STORE_BATCH_SIZE):
            store_batch = payload_items[j:j + STORE_BATCH_SIZE]
            if store_embeddings(store_batch):
                successful_batches += 1
                print(f"✅ Successfully stored batch {successful_batches}")
                time.sleep(BATCH_DELAY)  # Delay between store operations
            else:
                print("❌ Failed to store batch, will retry...")
                time.sleep(RATE_LIMIT_DELAY)
                # Retry once more
                if store_embeddings(store_batch):
                    successful_batches += 1
                    print(f"✅ Successfully stored batch {successful_batches} on retry")
            print(f"✅ Completed processing with {successful_batches} successful batches")
    print(f"✅ Total documents processed: {total_processed}")

    # save all tokens
    # log_token_count(token_count)
        


if __name__ == "__main__":
    try:
        clone_or_pull_repo(REPO_URL)
        copy_docs()
        rerun_embeddings()
        # log_token_count(101)
        print("✅ Successfully stored embeddings... ")

    except Exception as e:
        print(f"❌ Error: {e}")


