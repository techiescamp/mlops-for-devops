# MLOps for DevOps Engineers - A Hands-On Project

> **Bridge the gap between DevOps and Machine Learning Operations.**
> Follow the evolution of an ML project from a local prototype to a production-grade enterprise deployment.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 🎯 Use Case: Employee Attrition Prediction Model

Every phase in this repo uses the same real-world problem: **predicting employee attrition for a large organisation (~500,000 employees)**. This keeps the focus on *infrastructure and operations* rather than data-science theory.

| What you will build | Tools you will use |
|---|---|
| Data pipeline (ingest → clean → feature-store) | Python, Pandas, DVC |
| Trained ML model (scikit-learn / XGBoost) | scikit-learn, XGBoost |
| REST API for real-time inference | FastAPI, Docker |
| Scalable model serving on Kubernetes | KServe, Helm |
| Experiment tracking & model registry | MLflow |
| End-to-end ML pipeline orchestration | Kubeflow Pipelines |
| Observability & drift detection | Prometheus, Grafana, Evidently AI |

---

## 📋 Prerequisites

This repo assumes you already have a working knowledge of:

- **Linux** — command line, shell scripting, file systems
- **Docker** — building images, multi-stage builds, Docker Compose
- **Kubernetes** — deployments, services, ingress, Helm basics
- **CI/CD** — GitHub Actions or equivalent
- **Python** — basic scripting (you do *not* need ML experience)

If you need to brush up, see [docs/prerequisites.md](docs/prerequisites.md).

---

## 🗺️ Learning Path

```
Phase 1          Phase 2          Phase 3          Phase 4          Phase 5
─────────        ─────────        ─────────        ─────────        ─────────
 Local Dev   ──▶  Deploy &   ──▶  Enterprise  ──▶  Monitor &  ──▶  Foundation
 & Pipelines      Model Serve      Orchestrate      Observe          Models
```

### Phase 1 — Local Development & Data Pipelines
**Goal:** Build the ML foundation on your local machine.

| # | Task | Key Concept for DevOps Engineers |
|---|------|----------------------------------|
| 1.1 | Generate / download a 500 K-row synthetic dataset | Data versioning with **DVC** |
| 1.2 | Build an automated data pipeline (ingest → clean → feature engineering) | Reproducible pipelines, idempotency |
| 1.3 | Train a baseline model (Logistic Regression → XGBoost) | Understand artefact outputs (model files, metrics) |
| 1.4 | Evaluate the model and persist results | Metrics as code — think of it like test results in CI |

📂 **Code:** [`phase-1-local-dev/`](phase-1-local-dev/)
📖 **Guide:** [`phase-1-local-dev/README.md`](phase-1-local-dev/README.md)

---

### Phase 2 — Deployment & Model Serving
**Goal:** Turn a static `.pkl` file into a live, scalable service.

| # | Task | Key Concept for DevOps Engineers |
|---|------|----------------------------------|
| 2.1 | Wrap the model in a **FastAPI** REST API | Same as any microservice — health checks, versioning |
| 2.2 | Containerise with Docker (multi-stage build) | You already know this — just a different payload |
| 2.3 | Deploy to Kubernetes with **KServe** | Canary rollouts, autoscaling — model-specific CRDs |
| 2.4 | Load test the inference endpoint | Locust / k6 — same tools, ML-specific SLOs |

📂 **Code:** [`phase-2-deployment/`](phase-2-deployment/)
📖 **Guide:** [`phase-2-deployment/README.md`](phase-2-deployment/README.md)

---

### Phase 3 — Enterprise Orchestration (The MLOps Stack)
**Goal:** Automate training, tracking, and promotion of models.

| # | Task | Key Concept for DevOps Engineers |
|---|------|----------------------------------|
| 3.1 | Set up **MLflow** for experiment tracking & model registry | Think artifact repository (like Nexus/Artifactory but for models) |
| 3.2 | Build a **Kubeflow Pipeline** for end-to-end training | DAG-based pipelines — similar to Argo Workflows |
| 3.3 | Implement model promotion (staging → production) | GitOps-style gating with approvals |

📂 **Code:** [`phase-3-orchestration/`](phase-3-orchestration/)
📖 **Guide:** [`phase-3-orchestration/README.md`](phase-3-orchestration/README.md)

---

### Phase 4 — Model Observability & Monitoring
**Goal:** Ensure the deployed model stays healthy over time.

| # | Task | Key Concept for DevOps Engineers |
|---|------|----------------------------------|
| 4.1 | Expose Prometheus metrics from the inference service | Custom metrics: prediction latency, class distribution |
| 4.2 | Build Grafana dashboards for model health | Same Grafana you use today — new panels |
| 4.3 | Implement **data drift** and **model drift** detection | The ML equivalent of "the app is up but returning wrong results" |
| 4.4 | Set up alerting for drift thresholds | PagerDuty / Slack alerts when model degrades |

📂 **Code:** [`phase-4-monitoring/`](phase-4-monitoring/)
📖 **Guide:** [`phase-4-monitoring/README.md`](phase-4-monitoring/README.md)

---

### Phase 5 — The Shift to Foundational Models
**Goal:** Understand when to build vs. fine-tune vs. call an API.

| # | Topic | Key Concept for DevOps Engineers |
|---|-------|----------------------------------|
| 5.1 | Cost & complexity of custom model development | TCO analysis: training infra, data labelling, MLOps overhead |
| 5.2 | Fine-tuning foundational models | GPU provisioning, LoRA/QLoRA, model registries for LLMs |
| 5.3 | LLM serving infrastructure | vLLM, TGI, KServe with transformer runtime |
| 5.4 | RAG architecture patterns | Vector DBs, embeddings pipelines, caching layers |

📂 **Code:** [`phase-5-foundational-models/`](phase-5-foundational-models/)
📖 **Guide:** [`phase-5-foundational-models/README.md`](phase-5-foundational-models/README.md)

---

## 🏗️ Repo Structure

```
mlops-for-devops-engineers/
├── README.md                          # ← You are here
├── docs/
│   ├── prerequisites.md               # What you need before starting
│   ├── glossary.md                     # ML / MLOps terms for DevOps folk
│   └── architecture.md                # End-to-end system architecture
├── phase-1-local-dev/
│   ├── README.md                      # Phase guide
│   ├── data/                          # Data generation scripts & DVC config
│   ├── notebooks/                     # Exploratory analysis (optional)
│   ├── src/
│   │   ├── generate_data.py           # Synthetic 500K dataset generator
│   │   ├── data_pipeline.py           # Ingest → clean → feature engineering
│   │   ├── train.py                   # Model training script
│   │   └── evaluate.py               # Evaluation & metrics
│   └── tests/                         # Unit tests for pipeline
├── phase-2-deployment/
│   ├── README.md
│   ├── api/
│   │   ├── main.py                    # FastAPI inference service
│   │   ├── schemas.py                 # Request / response models
│   │   └── test_api.py               # API integration tests
│   ├── docker/
│   │   ├── Dockerfile                 # Multi-stage build
│   │   └── docker-compose.yml         # Local dev stack
│   └── kubernetes/
│       ├── kserve-inferenceservice.yaml
│       ├── namespace.yaml
│       └── load-test/
│           └── locustfile.py
├── phase-3-orchestration/
│   ├── README.md
│   ├── mlflow/
│   │   ├── docker-compose.yml         # MLflow server + PostgreSQL + MinIO
│   │   ├── train_with_tracking.py     # Training script with MLflow logging
│   │   └── register_model.py          # Model promotion script
│   └── kubeflow/
│       ├── pipeline.py                # Kubeflow Pipeline definition
│       └── components/                # Reusable pipeline components
├── phase-4-monitoring/
│   ├── README.md
│   ├── prometheus/
│   │   └── prometheus.yml             # Scrape config for model metrics
│   ├── grafana/
│   │   └── dashboards/
│   │       └── model-health.json      # Pre-built dashboard
│   └── drift-detection/
│       ├── detect_drift.py            # Evidently AI drift report
│       └── alert-rules.yml            # Prometheus alert rules
├── phase-5-foundational-models/
│   └── README.md                      # Discussion + reference architectures
├── scripts/
│   ├── setup-local.sh                 # One-command local setup
│   └── setup-k8s.sh                   # Kubernetes cluster bootstrap
└── .github/
    └── workflows/
        └── ci.yml                     # CI pipeline for the repo itself
```

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/<your-org>/mlops-for-devops-engineers.git
cd mlops-for-devops-engineers

# Run the one-command setup (creates venv, installs deps, generates data)
chmod +x scripts/setup-local.sh
./scripts/setup-local.sh

# Start Phase 1
cd phase-1-local-dev
cat README.md   # Follow the guide
```

---

## 🔑 Key Concepts — DevOps ↔ MLOps Mapping

This is the mental model that makes everything click. MLOps is not a new world — it is your existing world with a few new artefacts.

| DevOps Concept | MLOps Equivalent | What Changes |
|---|---|---|
| Source code | Source code **+ training data + model artefacts** | You now version data and models, not just code |
| Build artefact (JAR, binary) | **Trained model** (`.pkl`, `.onnx`, SavedModel) | The "build" is a training run that produces a model file |
| Unit tests | **Model evaluation** (accuracy, precision, recall) | Tests are statistical, not deterministic |
| CI pipeline | **Training pipeline** | Triggered by code *or data* changes |
| CD pipeline | **Model deployment pipeline** | Canary/shadow deployments are critical |
| Application logs | **Prediction logs + feature logs** | You log inputs, outputs, and feature values |
| APM / metrics | **Model monitoring + drift detection** | Latency matters, but so does prediction quality |
| Rollback | **Model rollback** | Revert to previous model version in registry |
| Config management | **Feature store + hyperparameters** | Config now includes data transformations |
| Artifact repo (Nexus) | **Model registry (MLflow)** | Stores models with metadata, lineage, stage labels |

---

## 📚 Recommended Reading

- [Google's MLOps Whitepaper (Practitioners Guide)](https://cloud.google.com/resources/mlops-whitepaper)
- [Made With ML — MLOps Course](https://madewithml.com/)
- [Chip Huyen — Designing ML Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)
- [DevOps to MLOps — DevOpsCube](https://devopscube.com/devops-to-mlops/)
- [ML Engineering for Production (Andrew Ng - Coursera)](https://www.coursera.org/specializations/machine-learning-engineering-for-production-mlops)

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
