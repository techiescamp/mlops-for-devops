# MLOps for DevOps Engineers

A hands-on, project-based guide to Machine Learning Operations — built specifically for DevOps, Platform, and SRE engineers.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/techiescamp/mlops-for-devops-engineers?style=social)](https://github.com/techiescamp/mlops-for-devops)

> **No ML background required.** Every concept is explained through DevOps analogies you already understand.

## Table of Contents

- [What Is This?](#what-is-this)
- [Use Case](#use-case)
- [Prerequisites](#prerequisites)
- [Learning Path](#learning-path)
  - [Phase 1 — Local Development \& Data Pipelines](#phase-1--local-development--data-pipelines)
  - [Phase 2 — Deployment \& Model Serving](#phase-2--deployment--model-serving)
  - [Phase 3 — Enterprise Orchestration](#phase-3--enterprise-orchestration)
  - [Phase 4 — Model Observability \& Monitoring](#phase-4--model-observability--monitoring)
  - [Phase 5 — Foundational Models](#phase-5--foundational-models)
- [Quick Start](#quick-start)
- [DevOps to MLOps — The Mental Model](#devops-to-mlops--the-mental-model)
- [Repo Structure](#repo-structure)
- [Tech Stack](#tech-stack)
- [Recommended Reading](#recommended-reading)
- [Contributing](#contributing)
- [License](#license)

## What Is This?

Most MLOps resources are written for data scientists learning infrastructure. This repo flips that — it is written for **infrastructure engineers learning ML operations**.

You do not need to become a data scientist. But just like understanding how a Java application is built makes you a better DevOps engineer, understanding how an ML model is built, trained, and served makes you effective at operating ML workloads in production.

This repo follows the complete lifecycle of an ML project — from a local prototype to a production-grade, monitored, enterprise deployment — with working code at every step.

## Use Case

Every phase uses the same real-world problem: **predicting employee attrition for a large organisation (~500,000 employees)**.

One use case, end to end. This keeps the focus on infrastructure and operations, not data-science theory.

## Prerequisites

| Skill | Level | Quick Check |
|-------|-------|-------------|
| Linux CLI | Intermediate | Can you write a bash script with loops and pipes? |
| Docker | Intermediate | Can you write a multi-stage Dockerfile? |
| Kubernetes | Intermediate | Can you deploy an app with Deployments, Services, and Ingress? |
| Python | Basic | Can you read Python code and run scripts? |
| Git | Intermediate | Can you branch, merge, and resolve conflicts? |

**No ML experience needed.** That is what this repo teaches.

See [docs/prerequisites.md](docs/prerequisites.md) for setup instructions.

## Learning Path

```
Phase 1          Phase 2          Phase 3          Phase 4          Phase 5
─────────        ─────────        ─────────        ─────────        ─────────
 Local Dev   ──▶  Deploy &   ──▶  Enterprise  ──▶  Monitor &  ──▶  Foundation
 & Pipelines      Model Serve      Orchestrate      Observe          Models
```

### Phase 1 — Local Development & Data Pipelines

**Goal:** Build the ML foundation on your local machine.

| Task | DevOps Analogy |
|------|----------------|
| Generate a 500K-row synthetic dataset | Data versioning with DVC (like Git LFS for data) |
| Build a data pipeline (ingest → clean → feature engineering) | Reproducible build pipeline, idempotent steps |
| Train a baseline model (Logistic Regression → XGBoost) | The "build" step — produces an artefact (model file) |
| Evaluate the model and persist metrics | Test results in CI — but statistical, not deterministic |

**Code:** [`phase-1-local-dev/`](phase-1-local-dev/) · **Guide:** [`phase-1-local-dev/README.md`](phase-1-local-dev/README.md)

---

### Phase 2 — Deployment & Model Serving

**Goal:** Turn a static `.pkl` file into a live, scalable service.

| Task | DevOps Analogy |
|------|----------------|
| Wrap the model in a FastAPI REST API | Standard microservice — health checks, Pydantic schemas |
| Containerise with Docker (multi-stage) | Same Docker workflow — just a different payload |
| Deploy to Kubernetes with KServe | CRD-based serving with canary rollouts and autoscaling |
| Load test the inference endpoint | Locust — same tools, ML-specific SLOs (latency, throughput) |

**Code:** [`phase-2-deployment/`](phase-2-deployment/) · **Guide:** [`phase-2-deployment/README.md`](phase-2-deployment/README.md)

---

### Phase 3 — Enterprise Orchestration

**Goal:** Automate training, tracking, and promotion of models.

| Task | DevOps Analogy |
|------|----------------|
| Set up MLflow for experiment tracking & model registry | Artifactory/Nexus for models + structured build logs |
| Build a Kubeflow Pipeline for end-to-end training | DAG-based pipelines — like Argo Workflows but ML-aware |
| Implement model promotion (Staging → Production) | GitOps-style gating with approval gates |

**Code:** [`phase-3-orchestration/`](phase-3-orchestration/) · **Guide:** [`phase-3-orchestration/README.md`](phase-3-orchestration/README.md)

---

### Phase 4 — Model Observability & Monitoring

**Goal:** Ensure the deployed model stays healthy over time.

| Task | DevOps Analogy |
|------|----------------|
| Expose Prometheus metrics from the inference service | Custom metrics — prediction latency, class distribution |
| Build Grafana dashboards for model health | Same Grafana, new panels |
| Implement data drift and model drift detection | "The app returns 200s but the answers are wrong" |
| Set up alerting for drift thresholds | PagerDuty / Slack alerts when model performance degrades |

**Code:** [`phase-4-monitoring/`](phase-4-monitoring/) · **Guide:** [`phase-4-monitoring/README.md`](phase-4-monitoring/README.md)

---

### Phase 5 — Foundational Models

**Goal:** Understand when to build custom models vs. fine-tune vs. call an API.

| Topic | DevOps Perspective |
|-------|-------------------|
| Cost & complexity of custom model development | TCO analysis — training infra, data labelling, MLOps overhead |
| Fine-tuning foundational models (LoRA/QLoRA) | GPU provisioning, checkpoint storage, distributed training |
| LLM serving infrastructure (vLLM, TGI, KServe) | GPU-aware scheduling, batching, autoscaling |
| RAG architecture patterns | Vector DBs, embeddings pipelines, caching layers |

**Code:** [`phase-5-foundational-models/`](phase-5-foundational-models/) · **Guide:** [`phase-5-foundational-models/README.md`](phase-5-foundational-models/README.md)

## Quick Start

```bash
# Clone
git clone https://github.com/techiescamp/mlops-for-devops-engineers.git
cd mlops-for-devops-engineers

# One-command setup (creates venv, installs deps, generates data, trains model)
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh

# Start learning
cd phase-1-local-dev && cat README.md
```

## DevOps to MLOps — The Mental Model

This is the single most important table in this repo. MLOps is not a new world — it is your existing world with a few new artefacts.

| DevOps Concept | MLOps Equivalent | What Changes |
|---|---|---|
| Source code | Source code + training data + model artefacts | You now version data and models, not just code |
| Build artefact (JAR, binary) | Trained model (`.pkl`, `.onnx`, SavedModel) | The "build" is a training run that produces a model file |
| Unit tests | Model evaluation (accuracy, precision, recall) | Tests are statistical, not deterministic |
| CI pipeline | Training pipeline | Triggered by code *or data* changes |
| CD pipeline | Model deployment pipeline | Canary/shadow deployments are critical |
| Application logs | Prediction logs + feature logs | You log inputs, outputs, and feature values |
| APM / metrics | Model monitoring + drift detection | Latency matters, but so does prediction quality |
| Rollback | Model rollback | Revert to previous model version in registry |
| Config management | Feature store + hyperparameters | Config now includes data transformations |
| Artifact repo (Nexus) | Model registry (MLflow) | Stores models with metadata, lineage, stage labels |

## Repo Structure

```
.
├── docs/
│   ├── prerequisites.md                # Setup instructions
│   ├── glossary.md                      # ML terms explained for DevOps engineers
│   └── architecture.md                 # End-to-end system architecture diagram
├── phase-1-local-dev/
│   ├── src/
│   │   ├── generate_data.py            # Synthetic 500K dataset generator
│   │   ├── data_pipeline.py            # Ingest → clean → feature engineering
│   │   ├── train.py                    # Model training (LogReg, RF, XGBoost)
│   │   └── evaluate.py                # Evaluation with quality gates
│   └── tests/                          # Unit tests for the pipeline
├── phase-2-deployment/
│   ├── api/
│   │   ├── main.py                     # FastAPI inference service
│   │   └── schemas.py                  # Request/response models
│   ├── docker/
│   │   ├── Dockerfile                  # Multi-stage build
│   │   └── docker-compose.yml          # Local dev stack (API + Prometheus)
│   └── kubernetes/
│       ├── kserve-inferenceservice.yaml # KServe CRD
│       └── load-test/locustfile.py     # Load testing
├── phase-3-orchestration/
│   ├── mlflow/
│   │   ├── docker-compose.yml          # MLflow + PostgreSQL + MinIO
│   │   ├── train_with_tracking.py      # Training with experiment logging
│   │   └── register_model.py           # Model promotion workflow
│   └── kubeflow/
│       └── pipeline.py                 # Kubeflow Pipeline definition
├── phase-4-monitoring/
│   ├── prometheus/prometheus.yml        # Scrape config for model metrics
│   ├── grafana/dashboards/             # Pre-built model health dashboard
│   └── drift-detection/
│       ├── detect_drift.py             # Evidently AI drift reports
│       └── alert-rules.yml             # Prometheus alerting rules
├── phase-5-foundational-models/
│   └── README.md                       # Build vs buy, LLM infra, RAG patterns
├── scripts/
│   └── setup-local.sh                  # One-command local setup
└── .github/workflows/
    └── ci.yml                          # CI pipeline with model quality gates
```

## Tech Stack

| Category | Tools |
|----------|-------|
| Data Pipeline | Python, Pandas, DVC |
| Model Training | scikit-learn, XGBoost |
| API / Serving | FastAPI, Docker, KServe |
| Orchestration | MLflow, Kubeflow Pipelines |
| Monitoring | Prometheus, Grafana, Evidently AI |
| Infrastructure | Kubernetes, Helm, GitHub Actions |
| LLM Serving (Phase 5) | vLLM, TGI, Ollama |

## Recommended Reading

- [Google MLOps Whitepaper](https://cloud.google.com/resources/mlops-whitepaper)
- [Made With ML — MLOps Course](https://madewithml.com/)
- [Designing Machine Learning Systems — Chip Huyen](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)
- [DevOps to MLOps — DevOpsCube](https://devopscube.com/devops-to-mlops/)
- [ML Engineering for Production — Andrew Ng (Coursera)](https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops)

See [docs/glossary.md](docs/glossary.md) for ML/MLOps terms explained through DevOps concepts.

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE).
