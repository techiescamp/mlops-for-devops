import re

# Amazon Nova Micro on-demand pricing (USD per 1M tokens)
_NOVA_MICRO_INPUT_PRICE_PER_1M  = 0.035
_NOVA_MICRO_OUTPUT_PRICE_PER_1M = 0.140

_REFUSAL_PATTERNS = re.compile(
    r"\b(i (don'?t|do not|cannot|can'?t) (know|answer|help|find|tell)|"
    r"(no|not enough) (information|context|data)|"
    r"out of (context|scope)|"
    r"i('?m| am) (not sure|unable)|"
    r"(sorry|apologies).{0,30}(can'?t|cannot|don'?t))\b",
    re.IGNORECASE,
)


def clamp_score(value):
    return float(max(0.0, min(1.0, value)))


def evaluate_faithfulness(bedrock_client, model_id, context, answer):
    """
    Evaluates how well the generated answer is grounded in the retrieved context using a judge LLM.
    """
    judge_prompt = f"""
    Context:
    {context}

    Answer:
    {answer}

    On a scale of 0 to 1, how well is the answer grounded in the context?
    Reply with only a number between 0 and 1. Do not include any explanation or additional text.
    """
    try:
        response = bedrock_client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": judge_prompt}]}]
        )
        score_text = response["output"]["message"]["content"][0]["text"]
        match = re.search(r"[-+]?\d*\.?\d+", score_text)
        if not match:
            raise ValueError(f"No numeric score found in judge response: {score_text}")
        return clamp_score(float(match.group(0)))
    except Exception as e:
        print(f"Faithfulness evaluation failed: {e}")
        return None

def compute_hallucination_rate(output, context):
    """
    Calculates the proportion of sentences in the output that have minimal word overlap with the context.
    """
    if not output or not context:
        return 0.0
    
    output_sentences = [p.strip() for p in re.split(r"[.!?]+", output) if p.strip()]
    if not output_sentences:
        return 0.0
        
    context_words = set(re.findall(r"\b\w+\b", context.lower()))
    hallucinated = 0

    for sent in output_sentences:
        sent_words = re.findall(r"\b\w+\b", sent.lower())
        if not sent_words:
            continue
        overlap = sum(1 for w in sent_words if w in context_words)
        if overlap < 3:  # fewer than 3 overlapping words -> likely hallucinated
            hallucinated += 1

    return clamp_score(hallucinated / len(output_sentences))


def evaluate_answer_relevance(bedrock_client, model_id, query, answer):
    """
    Evaluates how well the generated answer addresses the original query using a judge LLM.
    """
    judge_prompt = f"""
    Query:
    {query}

    Answer:
    {answer}

    On a scale of 0 to 1, how well does the answer address the query?
    Reply with only a number between 0 and 1. Do not include any explanation or additional text.
    """
    try:
        response = bedrock_client.converse(
            modelId=model_id,
            messages=[{"role": "user", "content": [{"text": judge_prompt}]}]
        )
        score_text = response["output"]["message"]["content"][0]["text"]
        match = re.search(r"[-+]?\d*\.?\d+", score_text)
        if not match:
            raise ValueError(f"No numeric score found in judge response: {score_text}")
        return clamp_score(float(match.group(0)))
    except Exception as e:
        print(f"Answer relevance evaluation failed: {e}")
        return None


def compute_cost(input_tokens, output_tokens,
                 input_price_per_1m=_NOVA_MICRO_INPUT_PRICE_PER_1M,
                 output_price_per_1m=_NOVA_MICRO_OUTPUT_PRICE_PER_1M):
    """
    Calculates USD cost of a single Bedrock LLM call from token counts.
    Defaults match Amazon Nova Micro on-demand pricing.
    """
    if input_tokens is None or output_tokens is None:
        return None
    cost = (input_tokens / 1_000_000) * input_price_per_1m + \
           (output_tokens / 1_000_000) * output_price_per_1m
    return round(cost, 8)


def compute_context_utilization(answer, context):
    """
    Fraction of answer words that appear in the retrieved context.
    High score means the answer stays grounded in what was retrieved.
    """
    if not answer or not context:
        return 0.0
    context_words = set(re.findall(r"\b\w+\b", context.lower()))
    answer_words  = re.findall(r"\b\w+\b", answer.lower())
    if not answer_words:
        return 0.0
    overlap = sum(1 for w in answer_words if w in context_words)
    return clamp_score(overlap / len(answer_words))


def detect_refusal(answer):
    """
    Returns 1.0 if the answer contains a refusal or fallback phrase, 0.0 otherwise.
    """
    if not answer:
        return 0.0
    return 1.0 if _REFUSAL_PATTERNS.search(answer) else 0.0
