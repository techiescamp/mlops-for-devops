import subprocess
import shutil
from pathlib import Path
import os
import requests
import glob
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
#  for hash code
import hashlib
import json

load_dotenv()

HASH_DB_PATH = Path("hash_files.json")

# # Load environment variables
# load_dotenv()
REPO_URL = os.environ["K8_URL"]
VECTOR_DB_URL = os.environ["VECTOR_DB_URL"]

# Constants
TEMP_DIR = Path(os.path.abspath("./temp-docs"))
TARGET_DIR = Path(os.path.abspath("./k8_docs/en"))

# Batch configuration
EMBEDDING_BATCH_SIZE = 100  # Reduced batch size for embeddings
STORE_BATCH_SIZE = 100     # Batch size for vector store uploads
BATCH_DELAY = 2          # Delay between batches in seconds
RATE_LIMIT_DELAY = 60    # Delay when hitting rate limits in seconds


# Configure retry strategy
retry_strategy = Retry(
    total=5,  # number of retries
    backoff_factor=1,  # wait 1, 2, 4, 8, 16 seconds between retries
    status_forcelist=[429, 500, 502, 503, 504]  # HTTP status codes to retry on
)
http_adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("http://", http_adapter)
session.mount("https://", http_adapter)


def clone_or_pull_repo():
    if not TEMP_DIR.exists():
        print("✅ Cloning Kubernetes docs repo...")
        subprocess.run(["git", "clone", REPO_URL, str(TEMP_DIR)], check=True)
    else:
        print("✅ Pulling latest changes...")
        subprocess.run(["git", "-C", str(TEMP_DIR), "pull"], check=True)


def copy_docs():
    base_dir = TEMP_DIR / "content" / "en" / "docs"
    # selected_subdirs = ["concepts", "reference", "setup", "tasks"]
    selected_subdirs = ["concepts"]

    print(f"Base directory: {base_dir}")
    print(f"Target directory: {TARGET_DIR}")

    for subdir in selected_subdirs:
        source_subdir = base_dir / subdir
        if not source_subdir.exists():
            print(f"⚠️ Source directory does not exist: {source_subdir}")
            continue

        print(f"✅ Copying docs from {source_subdir} to {TARGET_DIR}/{subdir}...")
        
        # Create the target subdirectory
        target_subdir = TARGET_DIR / subdir
        target_subdir.mkdir(parents=True, exist_ok=True)

        # Copy all markdown files with their directory structure
        for file in source_subdir.glob("**/*.md"):
            relative_path = file.relative_to(source_subdir)
            dest_file = target_subdir / relative_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, dest_file)
            print(f"📄 Copied: {file} -> {dest_file}")


def load_md_files():
    md_files = []
    try:
        search_path = os.path.join(TARGET_DIR, "concepts", "**", "*.md")
        print(f"Searching for markdown files in: {search_path}")
        for filepath in glob.glob(search_path, recursive=True):
            print(f"Found file: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            md_files.append({
                'filename': os.path.basename(filepath),
                'content': text,
            })
    except Exception as e:
        print(f"Error reading files: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")
    print(f"Loaded {len(md_files)} markdown files....")
    return md_files
        

def call_text_splitter(md_docs):
    print("Splitting documents into chunks...")
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
        
        # Safely print first document details if available
        if documents:
            first_doc = documents[0]
            try:
                print(f"First chunk sample - Content length: {len(first_doc.page_content)}")
                print(f"First chunk sample - Metadata: {first_doc.metadata}")
            except Exception as e:
                print(f"Warning: Could not print first document details: {e}")
                
        return documents
    except Exception as e:
        print(f"Error in text splitting: {e}")
        raise

def get_file_hash(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()

def load_existing_hashes():
    if HASH_DB_PATH.exists():
        with open(HASH_DB_PATH, "r") as f:
            return json.load(f)
    return {}

def save_hashes(hashes):
    with open(HASH_DB_PATH, "w") as f:
        json.dump(hashes, f, indent=2)


def process_and_store_batch(batch_documents):
    """Build the storage payload for a batch of documents (embedding happens in vector-store)."""
    payload = []
    for doc in batch_documents:
        try:
            payload.append({
                "metadata": doc.metadata,
                "content": doc.page_content
            })
        except Exception as e:
            print(f"Error accessing document content: {e}")
            continue

    return payload


def store_embeddings_batch(payload_batch):
    """Store a batch of embeddings in the vector store."""
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
    """ Recompute filename embeddings and save them. """
    print("🔁 Recomputing text embeddings for filenames...")

    #  initialize hash
    existing_hashes = load_existing_hashes()
    print('')
    new_hashes = {}
    to_embed = []

    # Document Loading Process
    md_files = load_md_files()
    print(f"Done with loading .md-files: {len(md_files)}")
    if md_files:
        print(f".md-files sample: {md_files[0]}")

    for doc in md_files:
        filename = doc['filename']
        content_hash = get_file_hash(doc["content"])
        new_hashes[filename] = content_hash

        if existing_hashes.get(filename) != content_hash:
            print(f"📌 Change detected: {filename}")
            to_embed.append(doc)
        else:
            print(f"✅ No change: {filename}")

    if not to_embed:
        print("🎉 All documents are up-to-date.")
        return

    print("Starting text splitting process...")
    try:
        # Text Splitting Process
        chunk_documents = call_text_splitter(to_embed)
        print(f"Done with splits: {len(chunk_documents)}")
        total_processed = 0
        successful_batches = 0

        # Process in batches
        for i in range(0, len(chunk_documents), EMBEDDING_BATCH_SIZE):
            batch = chunk_documents[i:i + EMBEDDING_BATCH_SIZE]
            print(f"\nProcessing batch {i//EMBEDDING_BATCH_SIZE + 1}/{(len(chunk_documents) + EMBEDDING_BATCH_SIZE - 1)//EMBEDDING_BATCH_SIZE}")
            
            # Generate embeddings for the batch
            payload_items = process_and_store_batch(batch)
            if not payload_items:
                print("Skipping empty batch...")
                continue
            
            total_processed += len(payload_items)
            print(f"Processed {total_processed} documents so far...")
            
            # Store embeddings in smaller sub-batches
            for j in range(0, len(payload_items), STORE_BATCH_SIZE):
                store_batch = payload_items[j:j + STORE_BATCH_SIZE]
                if store_embeddings_batch(store_batch):
                    successful_batches += 1
                    print(f"✅ Successfully stored batch {successful_batches}")
                    time.sleep(BATCH_DELAY)  # Delay between store operations
                else:
                    print("❌ Failed to store batch, will retry...")
                    time.sleep(RATE_LIMIT_DELAY)
                    # Retry once more
                    if store_embeddings_batch(store_batch):
                        successful_batches += 1
                        print(f"✅ Successfully stored batch {successful_batches} on retry")
        
        print(f"✅ Completed processing with {successful_batches} successful batches")
        print(f"✅ Total documents processed: {total_processed}")
        
        # Save file hashes after success
        save_hashes(new_hashes)
        
    except Exception as e:
        print(f"❌ Error during processing: {str(e)}")
        import traceback
        print("Traceback:")
        print(traceback.format_exc())
        raise

if __name__ == "__main__":
    try:
        clone_or_pull_repo()
        copy_docs()
        rerun_embeddings()
        print("✅ Successfully stored embeddings... ")
    except Exception as e:
        print(f"❌ Error: {e}")
