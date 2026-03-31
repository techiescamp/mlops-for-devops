FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    dvc \
    dvc-s3 \
    boto3 \
    pandas

WORKDIR /app

CMD ["python"]