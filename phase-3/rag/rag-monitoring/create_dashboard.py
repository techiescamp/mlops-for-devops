import json
import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False


load_dotenv(os.path.join(os.path.dirname(__file__), "../pipeline/.env"))

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
BEDROCK_LLM_MODEL = os.environ.get("BEDROCK_LLM_MODEL")
DASHBOARD_NAME = os.environ.get("RAG_DASHBOARD_NAME", "RAG-Local-Monitoring")


def text_widget(markdown, x, y, width=24, height=1):
    return {
        "type": "text",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "properties": {"markdown": markdown},
    }


def metric_widget(title, metrics, x, y, width=8, height=6, view="timeSeries", **extra):
    properties = {
        "metrics": metrics,
        "view": view,
        "stacked": False,
        "region": AWS_REGION,
        "title": title,
        "period": 300,
    }
    properties.update(extra)
    return {
        "type": "metric",
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "properties": properties,
    }


def bedrock_metric(metric_name, stat="Sum"):
    if not BEDROCK_LLM_MODEL:
        return None
    return ["AWS/Bedrock", metric_name, "ModelId", BEDROCK_LLM_MODEL, {"stat": stat}]


def compact_metrics(metrics):
    return [metric for metric in metrics if metric]


def build_dashboard_body():
    bedrock_invocations = bedrock_metric("Invocations", "Sum")
    bedrock_latency = bedrock_metric("InvocationLatency", "Average")
    bedrock_input_tokens = bedrock_metric("InputTokenCount", "Sum")
    bedrock_output_tokens = bedrock_metric("OutputTokenCount", "Sum")
    bedrock_throttles = bedrock_metric("InvocationThrottles", "Sum")
    bedrock_client_errors = bedrock_metric("InvocationClientErrors", "Sum")
    bedrock_server_errors = bedrock_metric("InvocationServerErrors", "Sum")

    widgets = [
        text_widget(
            "# RAG Monitoring - Local App to AWS CloudWatch\n"
            "Custom RAG metrics are pushed by the local app. Bedrock service metrics are read from AWS/Bedrock.",
            0,
            0,
            height=2,
        ),
        text_widget("## 1. Local RAG App - Custom Metrics", 0, 2),
        metric_widget(
            "End-to-End Query Latency",
            [
                ["RAG/Generation", "EndToEndLatency", {"stat": "Average", "label": "Average"}],
                [".", ".", {"stat": "p95", "label": "p95"}],
                [".", ".", {"stat": "p99", "label": "p99"}],
            ],
            0,
            3,
            width=12,
            yAxis={"left": {"min": 0}},
        ),
        metric_widget(
            "Stage Latency Split",
            [
                ["RAG/Retrieval", "RetrievalLatency", {"stat": "Average", "label": "Retrieval"}],
                ["RAG/Generation", "LLMLatency", {"stat": "Average", "label": "LLM generation"}],
                [".", "LLMLatencyBedrock", {"stat": "Average", "label": "Bedrock reported"}],
            ],
            12,
            3,
            width=12,
            yAxis={"left": {"min": 0}},
        ),
        text_widget("## 2. Retrieval and S3 Vector Store View", 0, 9),
        metric_widget(
            "Retrieval Health",
            [
                ["RAG/Retrieval", "RetrievedDocsCount", {"stat": "Average"}],
                ["RAG/VectorDB", "IndexHealthStatus", {"stat": "Average"}],
            ],
            0,
            10,
        ),
        metric_widget(
            "Retrieval Quality Proxies",
            [
                ["RAG/VectorDB", "AvgSimilarity", {"stat": "Average"}],
                [".", "PrecisionProxy", {"stat": "Average"}],
                [".", "RecallProxy", {"stat": "Average"}],
            ],
            8,
            10,
            view="gauge",
            yAxis={"left": {"min": 0, "max": 1}},
        ),
        metric_widget(
            "Vector Query Failures",
            [
                ["RAG/VectorDB", "QueryFailures", {"stat": "Sum"}],
                ["RAG/Retrieval", "RetrievalFailures", {"stat": "Sum"}],
            ],
            16,
            10,
        ),
        text_widget("## 3. Generation Quality - Custom RAG Metrics", 0, 16),
        metric_widget(
            "Groundedness and Hallucination",
            [
                ["RAG/Generation", "FaithfulnessScore", {"stat": "Average"}],
                [".", "HallucinationRate", {"stat": "Average"}],
            ],
            0,
            17,
            view="gauge",
            yAxis={"left": {"min": 0, "max": 1}},
        ),
        metric_widget(
            "Answer Relevance and Context Utilization",
            [
                ["RAG/Generation", "AnswerRelevance", {"stat": "Average", "label": "Answer Relevance"}],
                [".", "ContextUtilization", {"stat": "Average", "label": "Context Utilization"}],
            ],
            8,
            17,
            view="gauge",
            yAxis={"left": {"min": 0, "max": 1}},
        ),
        metric_widget(
            "Refusal Rate",
            [["RAG/Generation", "RefusalRate", {"stat": "Average"}]],
            16,
            17,
            view="singleValue",
            sparkline=True,
        ),
        metric_widget(
            "Response Length",
            [["RAG/Generation", "ResponseLength", {"stat": "Average"}]],
            0,
            23,
            view="singleValue",
            sparkline=True,
        ),
        metric_widget(
            "Cost Per Query (USD)",
            [["RAG/Generation", "CostPerQuery", {"stat": "Average", "label": "Avg cost"}]],
            8,
            23,
            view="timeSeries",
            yAxis={"left": {"min": 0}},
        ),
        metric_widget(
            "Custom Token Metrics",
            [
                ["RAG/Generation", "LLMInputTokens", {"stat": "Sum"}],
                [".", "LLMOutputTokens", {"stat": "Sum"}],
                [".", "LLMTotalTokens", {"stat": "Sum"}],
            ],
            16,
            23,
        ),
        metric_widget(
            "Hit Rate",
            [["RAG/Retrieval", "HitRate", {"stat": "Average"}]],
            0,
            29,
            view="singleValue",
            sparkline=True,
        ),
        text_widget("## 4. Indexing and Sync Metrics", 0, 35),
        metric_widget(
            "Embedding and Sync Progress",
            [
                ["RAG/Embeddings", "IndexSizeVectors", {"stat": "Maximum"}],
                [".", "EmbeddingVectorsLatency", {"stat": "Average"}],
                [".", "IndexFreshnessDays", {"stat": "Maximum"}],
            ],
            0,
            36,
            width=12,
        ),
        metric_widget(
            "Embedding and Ingestion Errors",
            [
                ["RAG/Embeddings", "IngestionError", {"stat": "Sum"}],
                [".", "EmbeddingError", {"stat": "Sum"}],
            ],
            12,
            36,
            width=12,
        ),
        text_widget("## 5. Amazon Bedrock Native Metrics", 0, 42),
    ]

    if BEDROCK_LLM_MODEL:
        widgets.extend(
            [
                metric_widget(
                    "Bedrock Invocations and Latency",
                    compact_metrics([bedrock_invocations, bedrock_latency]),
                    0,
                    43,
                    width=12,
                ),
                metric_widget(
                    "Bedrock Token Counts",
                    compact_metrics([bedrock_input_tokens, bedrock_output_tokens]),
                    12,
                    43,
                    width=12,
                ),
                metric_widget(
                    "Bedrock Service Errors and Throttles",
                    compact_metrics([bedrock_throttles, bedrock_client_errors, bedrock_server_errors]),
                    0,
                    49,
                    width=24,
                ),
            ]
        )
    else:
        widgets.append(
            text_widget(
                "Set BEDROCK_LLM_MODEL in pipeline/.env to include AWS/Bedrock native model metrics.",
                0,
                43,
                height=2,
            )
        )

    return {"widgets": widgets}


def create_rag_dashboard():
    import boto3

    cloudwatch = boto3.client("cloudwatch", region_name=AWS_REGION)
    dashboard_body = build_dashboard_body()

    try:
        cloudwatch.put_dashboard(
            DashboardName=DASHBOARD_NAME,
            DashboardBody=json.dumps(dashboard_body),
        )
        print(f"CloudWatch dashboard '{DASHBOARD_NAME}' created/updated successfully.")
    except Exception as e:
        print(f"Failed to create CloudWatch dashboard: {e}")
        raise


if __name__ == "__main__":
    create_rag_dashboard()
