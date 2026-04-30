import time
import statistics
import requests

FEAST_ENDPOINT = "http://<NODE-IP-HERE>:30566"


def fetch_features_with_latency(employee_ids, runs=50):
    """Fetch features from Feast and measure latency"""

    latencies = []

    for _ in range(runs):
        start = time.perf_counter()

        response = requests.post(
            f"{FEAST_ENDPOINT}/get-online-features",
            json={
                "features": [
                    "employee_features:age",
                    "employee_features:job_satisfaction",
                    "employee_features:work_life_balance",
                    "employee_features:overtime",
                ],
                "entities": {"employee_id": employee_ids},
            },
        )

        response.raise_for_status()

        elapsed_ms = (time.perf_counter() - start) * 1000
        latencies.append(elapsed_ms)

    latencies.sort()

    print(f"\nFeature Serving Latency ({runs} runs)")
    print(f"Min:  {min(latencies):.2f} ms")
    print(f"p50:  {statistics.median(latencies):.2f} ms")
    print(f"p95:  {latencies[int(len(latencies)*0.95)]:.2f} ms")
    print(f"p99:  {latencies[int(len(latencies)*0.99)]:.2f} ms")
    print(f"Max:  {max(latencies):.2f} ms")
    print(f"Mean: {statistics.mean(latencies):.2f} ms")


if __name__ == "__main__":
    sample_ids = [8410, 28098, 30257]

    print(f"Feast Endpoint: {FEAST_ENDPOINT}")
    fetch_features_with_latency(sample_ids, runs=100)