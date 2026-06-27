import os
import re
import json
import argparse
import shutil
import subprocess
import tempfile

import boto3
from dotenv import load_dotenv

# Load env variables from .env in workspace root
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

K8_REPO_URL = os.getenv("K8_REPO_URL")
K8_REPO_REF = os.getenv("K8_REPO_REF")
AWS_REGION = os.getenv("AWS_REGION")
BEDROCK_LLM_MODEL = os.getenv("BEDROCK_LLM_MODEL")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

K8_CONCEPTS_PATH = "content/en/docs/concepts"
# {{% code_sample file="..." %}} shortcodes in the concepts docs reference real
# YAML/JSON manifests that live in this sibling folder, not inline in the docs
# themselves - sparse-checked-out alongside concepts so resolve_code_samples()
# can read them locally instead of leaving the shortcode as dead placeholder text.
K8_EXAMPLES_PATH = "content/en/examples"

# Persistent clone location: cloned once, then `git pull`-ed on later runs
# instead of re-cloning from scratch every ingestion.
REPO_CLONE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'k8s-website-repo')

def clone_or_pull_repo(repo_url, clone_dir, remote_dirs, ref=None):
    """Clones only the `remote_dirs` subtrees on first run via git sparse-checkout
    (cone mode), or pulls latest changes on subsequent runs. Unlike a regular
    `git clone`, this avoids fetching blobs for the rest of the repository."""
    if not repo_url:
        raise ValueError("K8_REPO_URL is not configured.")
    if isinstance(remote_dirs, str):
        remote_dirs = [remote_dirs]

    if not os.path.exists(clone_dir):
        print(f"Cloning {repo_url} (sparse: {', '.join(remote_dirs)}) into {clone_dir}...")
        subprocess.run(
            ["git", "clone", "--filter=blob:none", "--no-checkout", repo_url, clone_dir],
            check=True
        )
        subprocess.run(["git", "-C", clone_dir, "sparse-checkout", "init", "--cone"], check=True)
    else:
        print(f"Pulling latest changes in {clone_dir}...")
        subprocess.run(["git", "-C", clone_dir, "pull"], check=True)

    # Re-applied on every run, not just on first clone, so an existing clone from
    # before content/en/examples was added picks up the new sparse path too.
    subprocess.run(["git", "-C", clone_dir, "sparse-checkout", "set", *remote_dirs], check=True)
    subprocess.run(["git", "-C", clone_dir, "checkout"], check=True)

    if ref:
        print(f"Checking out ref: {ref}...")
        subprocess.run(["git", "-C", clone_dir, "checkout", ref], check=True)

def copy_concepts_dir(clone_dir, remote_dir, output_dir):
    """Copies the concepts markdown subdirectory out of the full repo clone."""
    source_dir = os.path.join(clone_dir, remote_dir)
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(f"Source directory does not exist in repo: {source_dir}")

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir, exist_ok=True)

    copied = 0
    for root, _, files in os.walk(source_dir):
        for file in files:
            if not file.endswith('.md'):
                continue
            src_file = os.path.join(root, file)
            relative_path = os.path.relpath(src_file, source_dir)
            dest_file = os.path.join(output_dir, relative_path)
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            shutil.copy2(src_file, dest_file)
            copied += 1

    print(f"SUCCESS: Copied {copied} markdown files from {source_dir} to {output_dir}.")
    return copied

def merge_markdown_files(docs_dir, output_file, file_limit=50):
    """Recursively walks docs_dir and merges Markdown files into a single structured master Markdown file."""
    print(f"Merging Markdown files from: {docs_dir}")
    count = 0
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Sort folders/files for logical ordering
        for root, dirs, files in os.walk(docs_dir):
            dirs.sort()
            for file in sorted(files):
                if file.endswith('.md'):
                    if count >= file_limit:
                        print(f"Limit of {file_limit} files reached during merging.")
                        break

                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, docs_dir)
                    # Convert file path to semantic titles. _index.md is a folder's
                    # own landing page (Hugo convention), so its title is just the
                    # folder name rather than literally "... > _Index".
                    title_path = relative_path[:-len('.md')]
                    is_index = title_path.endswith('_index')
                    if is_index:
                        title_path = title_path[:-len('_index')].rstrip('/')
                    title = (title_path.replace('/', ' > ') or os.path.basename(docs_dir)).title()

                    # Heading level mirrors folder depth, so the tree we build later
                    # nests by folder (Workloads > Pods > ...) instead of treating every
                    # merged file as an unrelated top-level sibling. _index.md represents
                    # the folder itself; its sibling files nest one level deeper as children.
                    rel_dir = os.path.dirname(relative_path)
                    depth = 0 if rel_dir in ('', '.') else len(rel_dir.split(os.sep))
                    title_level = depth + 1 if is_index else depth + 2
                    shift = title_level - 1

                    outfile.write(f"\n\n{'#' * title_level} {title}\n\n")
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            for line in infile:
                                if shift > 0 and re.match(r'^#+\s', line):
                                    line = ('#' * shift) + line
                                outfile.write(line)
                        count += 1
                    except Exception as e:
                        print(f"Warning: Failed to read {file_path}: {e}")
            if count >= file_limit:
                break
    print(f"SUCCESS: Merged {count} Markdown files into {output_file}")
    return count

# The shortcode can carry other attributes before `file=` (e.g. `language="yaml"`),
# so this captures the whole attribute string and pulls `file="..."` out of it
# separately, rather than assuming `file` is always the first/only attribute.
CODE_SAMPLE_RE = re.compile(r'^[ \t]*\{\{%\s*code_sample\s+([^%]*?)\s*%\}\}[ \t]*$', re.MULTILINE)
FILE_ATTR_RE = re.compile(r'file="([^"]+)"')
LANG_BY_EXT = {'yaml': 'yaml', 'yml': 'yaml', 'json': 'json', 'sh': 'shell', 'txt': ''}

def resolve_code_samples(md_path, examples_root):
    """Replaces {{% code_sample file="..." %}} shortcode placeholders with the
    actual referenced manifest's content, read from the locally sparse-checked-out
    content/en/examples folder, wrapped in a fenced code block. Left unresolved,
    that placeholder line carries no actual content - it survives merging and
    heading-parsing as dead text, so an LLM asked e.g. "show me an example
    ConfigMap" would retrieve the literal shortcode string instead of real YAML.

    Returns (resolved_count, missing_count).
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    resolved = 0
    missing = 0

    def replace(match):
        nonlocal resolved, missing
        file_attr_match = FILE_ATTR_RE.search(match.group(1))
        if not file_attr_match:
            missing += 1
            return "_Example file reference could not be parsed._"

        # A handful of references use a leading "/" (e.g. "/controllers/x.yaml").
        # os.path.join() treats a leading-"/" second argument as absolute and
        # silently discards examples_root entirely, so strip it first.
        file_path = file_attr_match.group(1)
        full_path = os.path.join(examples_root, file_path.lstrip('/'))
        if not os.path.isfile(full_path):
            missing += 1
            return f"_Example file `{file_path}` could not be found._"

        with open(full_path, 'r', encoding='utf-8') as ef:
            file_content = ef.read().rstrip()

        resolved += 1
        ext = file_path.rsplit('.', 1)[-1].lower() if '.' in file_path else ''
        lang = LANG_BY_EXT.get(ext, ext)
        return f"```{lang}\n{file_content}\n```"

    new_content = CODE_SAMPLE_RE.sub(replace, content)

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"SUCCESS: Resolved {resolved} code_sample reference(s), {missing} missing, from {examples_root}.")
    return resolved, missing

def build_markdown_tree(md_path):
    """Parses a Markdown file's heading hierarchy (#, ##, ###...) into a nested
    tree structure compatible with extract_index_artifacts(). Each node's 'text'
    spans from its own heading through all of its descendants' content, so the
    node carries full context regardless of where tree traversal stops.

    Returns (tree, line_count).
    """
    with open(md_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    heading_re = re.compile(r'^(#{1,12})\s+(.*)')
    # Some headings here are entirely a Hugo `heading` shortcode call, e.g.
    # `## {{% heading "whatsnext" %}}`, which Hugo renders into localized boilerplate
    # text at build time. Parsed raw, that title would just be the shortcode literal -
    # map the known keys to their rendered English text instead.
    heading_shortcode_re = re.compile(r'^\{\{%\s*heading\s+"([\w-]+)"\s*%\}\}$')
    heading_shortcode_labels = {'whatsnext': "What's next", 'seealso': 'See also'}
    fence_re = re.compile(r'^\s*(```|~~~)')
    # Hugo shortcodes here mix delimiter styles ({{< tabs >}} ... {{% /tabs %}} has
    # been seen closing with the *other* style for the same block), so both '<'/'>'
    # and '%'/'%' are treated as equivalent delimiters for skip-depth tracking.
    shortcode_re = re.compile(r'^\s*\{\{[<%]\s*(/?)\s*([\w-]+).*?[>%]\}\}\s*$')

    # Most Hugo shortcodes here (figure, glossary_tooltip, glossary_definition...)
    # are self-contained one-liners with no closing tag. A few (tabs, tab, details,
    # note...) are real block wrappers with a matching closing tag. Only the latter
    # should affect skip-depth, or a never-closed tag would swallow the rest of the
    # document. Pre-scan to find which tag names are ever closed.
    paired_tags = {m.group(2) for m in (shortcode_re.match(l) for l in lines) if m and m.group(1) == '/'}

    headings = []  # (line_num, level, title), 1-indexed line numbers
    in_code_fence = False
    in_html_comment = False
    shortcode_depth = 0
    for i, line in enumerate(lines):
        if fence_re.match(line):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        if in_html_comment:
            if '-->' in line:
                in_html_comment = False
            continue
        if '<!--' in line:
            if '-->' not in line:
                in_html_comment = True
            continue

        m = shortcode_re.match(line)
        if m:
            slash, name = m.group(1), m.group(2)
            if name in paired_tags:
                shortcode_depth = max(0, shortcode_depth + (-1 if slash == '/' else 1))
            continue
        if shortcode_depth > 0:
            continue

        m = heading_re.match(line)
        if m:
            title = m.group(2).strip()
            sc_match = heading_shortcode_re.match(title)
            if sc_match:
                key = sc_match.group(1)
                title = heading_shortcode_labels.get(key, key.replace('-', ' ').title())
            headings.append((i + 1, len(m.group(1)), title))

    if not headings:
        return [], len(lines)

    node_counter = [0]

    def build_level(start_idx, level):
        """Builds sibling nodes at `level` starting from headings[start_idx]."""
        nodes = []
        i = start_idx
        while i < len(headings) and headings[i][1] >= level:
            line_num, _, title = headings[i]

            # Find the next heading at this level or shallower; that bounds this node's text.
            j = i + 1
            while j < len(headings) and headings[j][1] > level:
                j += 1
            end_line = headings[j][0] - 1 if j < len(headings) else len(lines)
            text = ''.join(lines[line_num - 1:end_line]).strip()

            node_counter[0] += 1
            node_id = f"{node_counter[0]:04d}"

            child_nodes = []
            if j > i + 1:
                child_level = min(h[1] for h in headings[i + 1:j])
                child_nodes = build_level(i + 1, child_level)

            nodes.append({
                'title': title,
                'node_id': node_id,
                'line_num': line_num,
                'text': text,
                'nodes': child_nodes
            })
            i = j
        return nodes

    top_level = min(h[1] for h in headings)
    tree = build_level(0, top_level)
    return tree, len(lines)

def extract_index_artifacts(full_structure):
    """Traverses full structure tree, separating headings structure (page_index) from text content (page_text)."""
    page_text = {}

    def _clean_and_extract(nodes):
        cleaned_nodes = []
        for node in nodes:
            line_num = node.get('line_num')
            text = node.get('text', '')
            if line_num is not None:
                page_text[str(line_num)] = text

            cleaned_node = {
                'title': node['title'],
                'node_id': node['node_id'],
                'line_num': line_num,
                'nodes': _clean_and_extract(node.get('nodes', []))
            }
            cleaned_nodes.append(cleaned_node)
        return cleaned_nodes

    page_index = _clean_and_extract(full_structure)
    return page_index, page_text

def upload_artifacts_to_s3(page_index, page_text, metadata):
    """Uploads JSON artifacts to S3."""
    print(f"Uploading index artifacts to S3 bucket: {S3_BUCKET_NAME}...")
    s3 = boto3.client('s3', region_name=AWS_REGION)

    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key='page_index.json',
        Body=json.dumps(page_index, indent=2, ensure_ascii=False)
    )
    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key='page_text.json',
        Body=json.dumps(page_text, indent=2, ensure_ascii=False)
    )
    s3.put_object(
        Bucket=S3_BUCKET_NAME,
        Key='metadata.json',
        Body=json.dumps(metadata, indent=2, ensure_ascii=False)
    )
    print("SUCCESS: Uploaded page_index.json, page_text.json, and metadata.json to S3.")

def run_ingestion(file_limit=200):
    # Setup paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_docs_dir = os.path.join(base_dir, 'backend', 'k8s-concepts')

    # 1. Sparse-clone the concepts dir and the examples dir it references via
    # {{% code_sample %}} shortcodes (or pull latest changes into the existing
    # persistent clone), then copy the concepts files out.
    clone_or_pull_repo(K8_REPO_URL, REPO_CLONE_DIR, [K8_CONCEPTS_PATH, K8_EXAMPLES_PATH], ref=K8_REPO_REF)
    copied_files = copy_concepts_dir(REPO_CLONE_DIR, K8_CONCEPTS_PATH, target_docs_dir)
    if copied_files == 0:
        raise FileNotFoundError(f"No files were copied from {K8_CONCEPTS_PATH}.")

    temp_dir = tempfile.mkdtemp()
    combined_md_path = os.path.join(temp_dir, 'combined_docs.md')

    try:
        # 2. Merge files
        num_merged = merge_markdown_files(target_docs_dir, combined_md_path, file_limit=file_limit)
        if num_merged == 0:
            print("No Markdown files found to index.")
            return

        # 3. Resolve {{% code_sample %}} placeholders into the actual referenced
        # YAML/JSON manifests before heading-parsing, so the real content - not
        # the dead shortcode text - is what gets indexed and retrieved.
        print("Resolving embedded code_sample examples...")
        examples_root = os.path.join(REPO_CLONE_DIR, K8_EXAMPLES_PATH)
        resolve_code_samples(combined_md_path, examples_root)

        # 4. Build a heading-based tree index locally (no external service needed)
        print("Building heading-based tree index from merged Markdown...")
        full_structure, line_count = build_markdown_tree(combined_md_path)

        # 5. Extract artifacts
        print("Extracting index and text artifacts...")
        page_index, page_text = extract_index_artifacts(full_structure)

        metadata = {
            'doc_name': 'Kubernetes Concepts Docs',
            'source_repo': K8_REPO_URL,
            'total_files_merged': num_merged,
            'line_count': line_count,
            'aws_region': AWS_REGION,
            'bedrock_model': BEDROCK_LLM_MODEL
        }

        # 6. Upload to S3
        upload_artifacts_to_s3(page_index, page_text, metadata)
        print("=== Ingestion Pipeline Complete! ===")

    finally:
        # Clean up temp folder
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ingest Kubernetes docs into a local heading-based tree index in S3')
    parser.add_argument('--limit', type=int, default=200, help='Maximum markdown files to merge')
    args = parser.parse_args()

    run_ingestion(file_limit=args.limit)
