# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies into /install directory
RUN pip install --upgrade pip \
    && pip install --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy project files
COPY index.py .
COPY components/ ./components/

CMD ["python3", "index.py"] 