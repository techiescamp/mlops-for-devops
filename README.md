# MLOps for DevOps Engineers

A hands-on, project-based guide to Machine Learning Operations built specifically for DevOps, Platform, and SRE engineers.

> No ML background required. Every concept is explained through DevOps analogies you already understand.

If you are completely new to MLOps, read our [DevOps to MLOps guide](https://devopscube.com) first.

---

## Table of Contents

- [Who This Is For](#who-this-is-for)
- [What We Build](#what-we-build)
- [Prerequisites](#prerequisites)
- [Learning Path](#learning-path)
- [Phase 1: Local Dev & Pipelines](#phase-1-local-development--data-pipelines)
- [Tech Stack](#tech-stack)
- [Recommended Reading](#recommended-reading)
- [License](#license)

---

## Who This Is For

Most MLOps resources are written for data scientists learning infrastructure. This repo flips that.

You do not need to become a data scientist. But just like understanding how a Java application is built makes you a better DevOps engineer, understanding how an ML model is built, trained, and served makes you effective at operating ML workloads in production.

---

## What We Build

| Track | What You Learn |
|-------|----------------|
| 🤖 Traditional ML | Train, serve, automate, and monitor a real ML model on Kubernetes |
| 🧠 Foundational Models | Serve LLMs in production using vLLM, TGI, and Ollama |
| ⚙️ LLM-Powered DevOps | Monitor K8s clusters, build RAG pipelines and agents with LLMs |

Everything runs on Kubernetes, Docker, and tools you already use.

---

## Prerequisites

| Skill | Level |
|-------|-------|
| Linux CLI | Intermediate |
| Docker | Intermediate |
| Kubernetes | Intermediate |
| AWS | Basic to Intermediate |
| Python | Basic — read and run scripts |
| Git | Intermediate |

No ML experience needed. That is what this repo teaches.

---

## Learning Path

| Phase | Track | Title | Status |
|-------|-------|-------|--------|
| 1 | 🤖 Traditional ML | [Local Dev & Pipelines](#phase-1-local-development--data-pipelines) | ✅ Done |
| 1 | 🤖 Traditional ML | K8s Deploy & Model Serving | ✅ Done |
| 3 | 🤖 Traditional ML | Enterprise Orchestration | 🔜 Planned |
| 4 | 🤖 Traditional ML | Monitor & Observe | 🔜 Planned |
| 5 | 🧠 Foundational Models | Foundational Models | 🔜 Planned |
| 6 | 🧠 Foundational Models | LLM Serving & Scaling | 🔜 Planned |
| 7 | ⚙️ LLM-Powered DevOps | LLM-Powered DevOps | 🔜 Planned |
| 8 | ⚙️ LLM-Powered DevOps | Emerging AI Ops | 🔜 Planned |

---

## Phase 1: Local Development & Data Pipelines

**Goal:** Build the full ML foundation on your local machine — from raw data to a trained, tested model.

**Use case throughout:** Employee attrition prediction for a large organisation (~500,000 employees). One problem, end to end. Keeps the focus on infrastructure and operations, not data science theory.

| Step | Title | Guide |
|------|-------|-------|
| 1 | Project Dataset Pipeline | [Read the Guide](https://newsletter.devopscube.com/p/building-a-dataset-pipeline) |
| 2 | Data Preparation Stages | [Read the Guide](https://newsletter.devopscube.com/p/mlops-data-preparation) |
| 3 | Training & Building the Prediction Model | [Read the Guide](https://newsletter.devopscube.com/p/mlops-training-the-model) |
| 4 | From Model to Live API with KServe | [Read the Guide](https://newsletter.devopscube.com/p/deploying-model-kserve) |

Code: `phase-1-local-dev/`

## Phase 2: Enterprise Orchestration for ML

**Goal:** Build the full ML pipeline using CNCF ML tooling

🔜 Coming this Saturday

---

## Tech Stack

| Category | Tools |
|----------|-------|
| Data Pipeline | Python, Pandas |
| Model Training | scikit-learn, XGBoost |
| API / Serving | FastAPI, Docker, KServe |
| Orchestration | MLflow, Kubeflow Pipelines |
| Monitoring | Prometheus, Grafana, Evidently AI |
| Infrastructure | Kubernetes, Helm, GitHub Actions |
| LLM Serving | vLLM, TGI, Ollama |

---

## Recommended Reading

- [Google MLOps Whitepaper](https://cloud.google.com/resources/mlops-whitepaper)
- [Volkswagen's End-to-End MLOps Platform on AWS](https://aws.amazon.com/solutions/case-studies/volkswagen-mlops/)

## Certifications

- [AWS Certified Machine Learning Engineer - Associate](https://aws.amazon.com/certification/certified-machine-learning-engineer-associate/)
- [Nvidia AI Infrastructure and Operations](https://www.nvidia.com/en-us/training/)

---

## License

Dual licensed:

- **Code** (scripts, configs, manifests) — Apache 2.0
- **Content** (README, guides, docs) — All Rights Reserved

For commercial licensing: contact@devopscube.com
