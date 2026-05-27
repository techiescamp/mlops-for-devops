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
TARGET_DIR = Path(os.path.abspath("./k8_docs/en"))


def clone_or_pull_repo(REPO_URL):
    if not TEMP_DIR.exists():
        print("✅ Cloning Kubernetes docs repo...")
        subprocess.run(["git", "clone", REPO_URL, str(TEMP_DIR)], check=True)
    else:
        print("✅ Pulling latest changes...")
        subprocess.run(["git", "-C", str(TEMP_DIR), "pull"], check=True)


def  copy_docs():
    base_dir = TEMP_DIR / "content" / "en" / "docs"
    selected_dirs = ["concepts"]

    print(f"Base directory: {base_dir}")
    print(f"Target directory: {TARGET_DIR}")

    for subdir in selected_dirs:
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
                'filepath': os.path.relpath(filepath, TARGET_DIR),
                'content': text,
            })
        print(f"Loaded {len(md_files)} markdown files")
        # Loaded 154 markdown files
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

