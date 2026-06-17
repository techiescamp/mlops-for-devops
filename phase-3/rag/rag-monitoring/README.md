# RAG Monitoring with AWS CloudWatch

This folder contains the CloudWatch monitoring utilities for the local RAG app.

The current architecture is intentionally simple:

```text
Local React frontend
        |
Local FastAPI backend / indexing scripts
        |
        | calls
        v
Amazon Bedrock + S3 Vector Store

Local app code
        |
        | PutMetricData
        v
CloudWatch custom metrics

Amazon Bedrock
        |
        | AWS service metrics
        v
CloudWatch AWS/Bedrock metrics

CloudWatch Metrics
        |
        v
CloudWatch Dashboard
```

This monitoring scope focuses on metric collection and dashboard visualization.

## Files

- `cloudwatch_client.py`: small wrapper around CloudWatch `put_metric_data`.
- `retrieval_metrics.py`: retrieval quality proxy calculations from S3 Vector query distances.
- `generation_metrics.py`: faithfulness scoring and hallucination-rate helper functions.
- `create_dashboard.py`: creates a CloudWatch dashboard for the local RAG monitoring view.

## Metric Sources

### Custom RAG Metrics

These metrics are pushed by the local pipeline/backend code through `push_metric()`.

`RAG/Embeddings`

- `IndexSizeVectors`
- `EmbeddingVectorsLatency`
- `IndexFreshnessDays`
- `IngestionError`
- `EmbeddingError`

`RAG/VectorDB`

- `QueryLatency`
- `AvgSimilarity`
- `PrecisionProxy`
- `RecallProxy`
- `QueryFailures`
- `IndexHealthStatus`

`RAG/Retrieval`

- `RetrievalLatency`
- `RetrievalFailures`
- `RetrievedDocsCount`

`RAG/Generation`

- `EndToEndLatency`
- `LLMLatency`
- `LLMLatencyBedrock`
- `FaithfulnessScore`
- `HallucinationRate`
- `LLMInputTokens`
- `LLMOutputTokens`
- `LLMTotalTokens`
- `ResponseLength`

### AWS Bedrock Native Metrics

The dashboard can also show AWS-native Bedrock metrics from `AWS/Bedrock` when `BEDROCK_LLM_MODEL` is present in `pipeline/.env`.

Examples:

- `Invocations`
- `InvocationLatency`
- `InputTokenCount`
- `OutputTokenCount`
- `InvocationThrottles`
- `InvocationClientErrors`
- `InvocationServerErrors`

## Create or Update the Dashboard

From this folder:

```bash
python create_dashboard.py
```

The dashboard name defaults to:

```text
RAG-Local-Monitoring
```

You can override it with:

```text
RAG_DASHBOARD_NAME
```

## Notes

- Retrieval precision and recall are proxy metrics, not ground-truth evaluation metrics.
- Hallucination rate is a lightweight lexical heuristic.
- Faithfulness uses a Bedrock judge model call.
- S3 Vector Store quality is measured from the app's returned distances and result counts, not from a guaranteed AWS-native S3 Vectors CloudWatch namespace.
