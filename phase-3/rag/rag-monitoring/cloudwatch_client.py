import boto3
from datetime import datetime, timezone
import os

class RAGCloudWatchLogger:
    def __init__(self, region_name=None, namespace='RAG/Custom'):
        self.region_name = region_name or os.environ.get("AWS_REGION", "us-east-1")
        self.namespace = namespace
        self.cloudwatch = boto3.client("cloudwatch", region_name=self.region_name)

    def push_metric(self, name, value, unit='None', namespace=None, dimensions=None):
        """
        Pushes a custom metric to Amazon CloudWatch.
        """
        ns = namespace or self.namespace
        metric_data = {
            "MetricName": name,
            "Timestamp": datetime.now(timezone.utc),
            "Value": float(value),
            "Unit": str(unit) if unit else "None"
        }
        if dimensions:
            metric_data["Dimensions"] = dimensions

        try:
            self.cloudwatch.put_metric_data(
                Namespace=ns,
                MetricData=[metric_data]
            )
            print(f"Successfully pushed metric {name}={value} to namespace {ns}")
            return True
        except Exception as e:
            print(f"CloudWatch metric push failed for {name}: {e}")
            return False

# Export a simple default function compatible with the blog's syntax
_default_logger = None

def push_metric(name, value, unit='None', namespace='RAG/Custom', dimensions=None):
    global _default_logger
    if _default_logger is None:
        _default_logger = RAGCloudWatchLogger()
    return _default_logger.push_metric(name, value, unit, namespace, dimensions)
