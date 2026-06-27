import os
import re
import json
import boto3
from dotenv import load_dotenv

# Load env variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

AWS_REGION = os.getenv("AWS_REGION")
BEDROCK_LLM_MODEL = os.getenv("BEDROCK_LLM_MODEL")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# Initialize AWS clients
s3_client = boto3.client('s3', region_name=AWS_REGION)
bedrock_client = boto3.client('bedrock-runtime', region_name=AWS_REGION)

def invoke_nova(prompt: str, max_tokens: int = 1024) -> str:
    """Wrapper to invoke Bedrock Nova Micro model."""
    body = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": 0.0
        }
    }
    
    response = bedrock_client.invoke_model(
        modelId=BEDROCK_LLM_MODEL,
        body=json.dumps(body)
    )
    response_body = json.loads(response.get('body').read())
    return response_body['output']['message']['content'][0]['text']

def clean_json_response(text: str) -> str:
    """Cleans potential Markdown wrap from JSON outputs."""
    text = text.strip()
    # Remove markdown code blocks if present
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?", "", text)
        text = re.sub(r"```$", "", text)
    return text.strip()

def get_s3_json(key: str) -> dict:
    """Helper to download a JSON file from S3."""
    response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=key)
    return json.loads(response['Body'].read().decode('utf-8'))

def traverse_tree(query: str, page_index: list) -> tuple[list, list]:
    """
    LLM-guided tree navigation loop. 
    Nova Micro is prompted to select which sub-nodes are relevant at each level of the tree.
    """
    current_nodes = page_index
    path_taken = []
    selected_leaf_nodes = []

    # Budget only counts levels where the model actually had to make a choice.
    # Single-candidate hops (e.g. the tree root) are free since there's nothing
    # to decide - otherwise topics nested deeper than the budget purely because
    # of structural single-child folders (no real ambiguity) would get cut off
    # before reaching their actual content, as happened with "Deployment" (6
    # heading levels deep) under the old fixed 5-iteration cap.
    MAX_LLM_LEVELS = 8
    llm_levels_used = 0

    while current_nodes and llm_levels_used < MAX_LLM_LEVELS:
        level = llm_levels_used

        # No real decision to make with a single candidate (e.g. the tree root,
        # which is just one "K8S-Concepts" node) - asking the model to echo back
        # an exact ID it has nothing to disambiguate from is an unnecessary point
        # of failure (a small model can still get the ID wrong even with no other
        # options), so just descend into it directly without an LLM call or
        # spending any of the depth budget.
        if len(current_nodes) == 1:
            only = current_nodes[0]
            path_taken.append({"title": only["title"], "node_id": only["node_id"]})
            if only.get("nodes"):
                current_nodes = only["nodes"]
                continue
            selected_leaf_nodes.append(only)
            break

        llm_levels_used += 1

        # Compile nodes list at the current level. Title alone is often too
        # ambiguous for the small navigator model (e.g. "Containers" vs
        # "Workloads" both sound plausible for a Pod query) - a preview of each
        # branch's immediate children gives it the extra signal to disambiguate
        # without having to fully drill down first.
        options = []
        for node in current_nodes:
            option = {
                "node_id": node["node_id"],
                "title": node["title"],
                "line_num": node.get("line_num")
            }
            children = node.get("nodes") or []
            if children:
                option["subsections"] = [c["title"] for c in children[:10]]
            options.append(option)
            
        path_desc = " -> ".join([p["title"] for p in path_taken]) if path_taken else "Root"
        
        prompt = f"""You are navigating a technical documentation index tree to answer this user query:
"{query}"

Current navigation path: {path_desc}

Here are the documentation sub-sections available at the current level. Where present, "subsections"
lists that section's own immediate children - use it to judge what a section actually contains,
since the title alone can be misleading (e.g. a query about Pods may relate to several sibling
sections by topic, but only one actually contains Pod content). A title ending in "[overview]"
means: stop here, this section's own content already covers the topic broadly - prefer it over
drilling into one specific subsection unless the query asks for something narrower that only a
subsection would cover:
{json.dumps(options, indent=2)}

Task: Identify which section ID(s) (node_id) are highly relevant to finding the answer to the query.
Instructions:
1. Select one or more relevant 'node_id' values from the list above.
2. Return your response strictly as a JSON list of strings containing the IDs, for example: ["0012", "0015"].
3. If none of the sections are relevant, or if the current sections are the final pages containing the answer itself, return an empty list: [].
4. Return ONLY the JSON list. Do not include any explanations, introduction, markdown blocks, or surrounding text.
"""
        try:
            raw_response = invoke_nova(prompt, max_tokens=100)
            cleaned = clean_json_response(raw_response)
            selected_ids = json.loads(cleaned)
            
            if not isinstance(selected_ids, list):
                print(f"Warning: Selected IDs is not a list: {selected_ids}. Stopping traversal.")
                break
                
            if not selected_ids:
                # The LLM returned an empty list, indicating current level nodes are the leaf targets
                selected_leaf_nodes.extend(current_nodes)
                break
                
            # Filter matches and drill down
            next_level_nodes = []
            matched_any = False
            for node in current_nodes:
                if node["node_id"] in selected_ids:
                    matched_any = True
                    path_taken.append({"title": node["title"], "node_id": node["node_id"]})

                    children = node.get("nodes")
                    if children:
                        # Give the model the choice between drilling into one specific
                        # subsection or using this section's own content - which, per
                        # build_markdown_tree, already spans this entire subtree - as a
                        # sufficient answer on its own. Without this, the navigator always
                        # drilled to the deepest leaf even when an ancestor already held
                        # the actual definition (e.g. "Deployment" kept descending into a
                        # narrow rollout-strategy leaf instead of stopping at the section
                        # that defines what a Deployment is).
                        next_level_nodes.append({
                            "title": f"{node['title']} [overview]",
                            "node_id": f"{node['node_id']}-self",
                            "line_num": node.get("line_num"),
                            "nodes": []
                        })
                        next_level_nodes.extend(children)
                    else:
                        # No children, this is a leaf node
                        selected_leaf_nodes.append(node)

            # The model returned ID(s) that don't match anything at this level
            # (hallucinated IDs are a known risk with a small model). Treating
            # this as "everything here is relevant" used to dump every sibling's
            # full subtree text into context, which is large enough to blow past
            # Bedrock's input token limit. Safer to just stop with whatever was
            # already found rather than silently widening scope.
            if not matched_any:
                print(f"Warning: Selected IDs {selected_ids} matched no node at level {level}. Stopping traversal.")
                break

            current_nodes = next_level_nodes

        except Exception as e:
            print(f"Error during tree traversal at level {level}: {e}")
            break
            
    # Deduplicate leaf nodes
    unique_leaves = []
    seen_ids = set()
    for node in selected_leaf_nodes:
        if node["node_id"] not in seen_ids:
            seen_ids.add(node["node_id"])
            unique_leaves.append(node)
            
    return unique_leaves, path_taken

def query_vectorless_rag(query: str) -> dict:
    """Main query entrypoint to perform tree traversal, fetch exact pages, and generate answer."""
    print(f"=== Starting Query RAG Pipeline ===")
    print(f"User Query: {query}")
    
    # 1. Download index structure from S3
    try:
        page_index = get_s3_json('page_index.json')
    except Exception as e:
        return {
            "answer": f"Error: Could not retrieve the document index from S3: {e}. Please make sure the ingestion pipeline has been run first.",
            "path_taken": [],
            "citations": []
        }
        
    # 2. Traverse tree using Bedrock to identify targeted pages
    print("Navigating document structure index using Bedrock reasoning...")
    target_nodes, path_taken = traverse_tree(query, page_index)
    
    if not target_nodes:
        return {
            "answer": "The reasoning agent could not locate any relevant sections in the documentation index.",
            "path_taken": path_taken,
            "citations": []
        }
        
    print(f"Reasoning complete. Selected {len(target_nodes)} sections to retrieve content.")
    
    # 3. Download flat page text from S3
    try:
        page_text = get_s3_json('page_text.json')
    except Exception as e:
        return {
            "answer": f"Error: Failed to fetch exact page text from S3: {e}",
            "path_taken": path_taken,
            "citations": []
        }
        
    # 4. Fetch the exact pages matching target nodes
    context_parts = []
    citations = []
    
    # Hard cap on how much retrieved text gets sent to the compose step. A single
    # selected node's text can span its entire subtree (see build_markdown_tree),
    # so without a cap a legitimately-matched but broad section can still produce
    # a prompt large enough to exceed Bedrock's input token limit.
    MAX_SECTION_CHARS = 6000
    MAX_TOTAL_CONTEXT_CHARS = 40000
    total_chars = 0

    for node in target_nodes:
        ln = str(node.get("line_num"))
        text = page_text.get(ln, "")
        if not text.strip():
            continue
        if total_chars >= MAX_TOTAL_CONTEXT_CHARS:
            print(f"Warning: Context budget reached, dropping remaining sections starting at '{node['title']}'.")
            break

        truncated = text[:MAX_SECTION_CHARS]
        context_parts.append(f"--- Section: {node['title']} (Line: {ln}) ---\n{truncated}")
        citations.append({
            "title": node["title"],
            "line_num": node.get("line_num"),
            "node_id": node["node_id"],
            "text": truncated
        })
        total_chars += len(truncated)
            
    if not context_parts:
        return {
            "answer": "The reasoning agent located relevant section names, but no text content was found for those lines.",
            "path_taken": path_taken,
            "citations": citations
        }
        
    # 5. Compose the final answer using exact pages
    context_text = "\n\n".join(context_parts)
    print("Generating response using context sections...")
    
    compose_prompt = f"""You are a professional documentation assistant. Answer the user query using ONLY the retrieved sections below.

Retrieved Documentation Sections:
{context_text}

Query: "{query}"

Instructions:
1. Base your answer strictly on the facts in the retrieved sections. If the context does not contain enough info, state that the information was not found.
2. For each fact or quote you state, you MUST explicitly cite which section it came from by mentioning its title and line number in parentheses, e.g., (from Section: Kubernetes Networking, Line: 154).
3. Do not formulate explanations that aren't backed by the text.
"""
    
    try:
        answer = invoke_nova(compose_prompt, max_tokens=1500)
    except Exception as e:
        answer = f"Error generating answer: {e}"
        
    return {
        "answer": answer,
        "path_taken": path_taken,
        "citations": citations
    }

if __name__ == "__main__":
    # Local CLI test
    import sys
    test_query = "What is a Pod?" if len(sys.argv) < 2 else sys.argv[1]
    res = query_vectorless_rag(test_query)
    print("\n=== ANSWER ===")
    print(res["answer"])
    print("\n=== PATH TAKEN ===")
    print(" -> ".join([p["title"] for p in res["path_taken"]]))
    print("\n=== CITATIONS ===")
    print(res["citations"])
