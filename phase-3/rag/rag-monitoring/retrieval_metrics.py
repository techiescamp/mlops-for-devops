import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def clamp_score(value):
    return float(max(0.0, min(1.0, value)))

def normalize_similarity(distance, metric='COSINE'):
    """
    Convert S3 Vector distance to similarity score (0-1).
    - COSINE: similarity = 1 - distance
    - EUCLIDEAN: similarity = 1 / (1 + distance)
    """
    if distance is None:
        return 0.0
    if metric.upper() == 'COSINE':
        return clamp_score(1.0 - float(distance))
    elif metric.upper() == 'EUCLIDEAN':
        if distance < 0:
            return 0.0
        return clamp_score(1.0 / (1.0 + float(distance)))
    else:
        return 0.0

def compute_similarity_and_precision_like(payload, metric='COSINE', top_weighted=False):
    """
    Calculates retrieval quality proxy metrics from S3 Vector distance scores.
    payload: list of retrieved docs with 'score' key.
    """
    scores = [doc.get('score') for doc in payload if doc.get('score') is not None]
    if not scores:
        avg_similarity = 0.0
        precision_like = 0.0
    else:
        similarities = [normalize_similarity(d, metric) for d in scores]
        avg_similarity = float(np.mean(similarities))
        if top_weighted:
            weights = np.linspace(len(similarities), 1, len(similarities))
            precision_like = float(np.average(similarities, weights=weights))
        else:
            precision_like = avg_similarity
    return avg_similarity, precision_like

def compute_recall_like(vectors):
    """
    Measures diversity among top-K retrieved chunks as a recall-like proxy.
    vectors: list of vector dicts from S3 Vectors query response.
    """
    retrieved_vecs = [np.array(v['data']['float32']) for v in vectors if v.get('data') and 'float32' in v['data']]
    if len(retrieved_vecs) < 2:
        return 0.0
    sims = cosine_similarity(retrieved_vecs)
    np.fill_diagonal(sims, 0)
    diversity = 1.0 - np.mean(sims)  # higher = more diversity
    return clamp_score(diversity)


def compute_hit(num_docs):
    """
    Returns 1.0 if at least one document was retrieved, 0.0 otherwise.
    """
    return 1.0 if num_docs and num_docs > 0 else 0.0
