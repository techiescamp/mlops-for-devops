import os
import shutil
import subprocess
import json
import hashlib
import glob
import datetime
from pathlib import Path


TOKEN_LOG_FILE = Path("token_log.json")
HASH_DB_PATH = Path("hash_files.json")
TEMP_DIR = Path(os.path.abspath("./temp-docs"))
TARGET_DIR = Path(os.path.abspath("./repo_docs"))


def clone_or_pull_repo(repo_url):
    if not TEMP_DIR.exists():
        print(f"✅ Cloning docs repo: {repo_url}")
        subprocess.run(["git", "clone", repo_url, str(TEMP_DIR)], check=True)
    else:
        print("✅ Pulling latest changes...")
        subprocess.run(["git", "-C", str(TEMP_DIR), "pull"], check=True)


def copy_docs():
    """Copy every .md file found under REPO_DOCS_PATH (or the whole repo, if
    unset) into TARGET_DIR, preserving each file's path relative to the source
    root. Leaving REPO_DOCS_PATH unset works for any repo's layout with no
    assumptions about a fixed docs folder; setting it scopes indexing to a
    specific subfolder (e.g. content/en/docs/concepts for kubernetes/website),
    which also avoids pulling in translated docs, blog posts, etc."""
    docs_subpath = os.environ.get("REPO_DOCS_PATH", "").strip().strip("/")
    source_root = (TEMP_DIR / docs_subpath) if docs_subpath else TEMP_DIR

    print(f"Source directory: {source_root}")
    print(f"Target directory: {TARGET_DIR}")

    if not source_root.exists():
        print(f"⚠️ REPO_DOCS_PATH does not exist in repo: {source_root}")
        return

    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    copied = 0
    for file in source_root.glob("**/*.md"):
        relative_path = file.relative_to(source_root)
        dest_file = TARGET_DIR / relative_path
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest_file)
        copied += 1

    print(f"✅ Copied {copied} markdown files to {TARGET_DIR}")


def load_md_files():
    md_files = []
    try:
        search_path = os.path.join(TARGET_DIR, "**", "*.md")
        print(f"Searching for markdown files in: {search_path}")
        for filepath in glob.glob(search_path, recursive=True):
            print(f"Found file: {filepath}")
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            md_files.append({
                'filename': os.path.basename(filepath),
                'filepath': os.path.relpath(filepath, TARGET_DIR),
                'content': text,
            })
        print(f"Loaded {len(md_files)} markdown files")
        return md_files
    except Exception as e:
        print(f"Error reading files: {str(e)}")
        print(f"Current working directory: {os.getcwd()}")


def load_existing_hashes():
    if HASH_DB_PATH.exists():
        with open(HASH_DB_PATH, "r") as f:
            return json.load(f)
    return {}


def get_hash_file(content):
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def save_hashes(hashes):
    with open(HASH_DB_PATH, "w") as f:
        json.dump(hashes, f, indent=2)


def log_token_count(token_count):
    if os.path.exists(TOKEN_LOG_FILE):
        with open(TOKEN_LOG_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = []
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tokens_used": token_count
    }
    data.append(entry)
    with open(TOKEN_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("🎉 Token Count logged")
