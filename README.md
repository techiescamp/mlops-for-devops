# MLOps for DevOps Engineers

A hands-on, project-based guide to Machine Learning Operations built specifically for DevOps, Platform, and SRE engineers.

> No ML background required. Every concept is explained through DevOps analogies you already understand.

If you are completely new to MLOps, read our [DevOps to MLOps guide](https://devopscube.com/devops-to-mlops/) first.

---

## Table of Contents

- [Who This Is For](#who-this-is-for)
- [What We Build](#what-we-build)
- [Prerequisites](#prerequisites)
- [Phase 1: Local Dev & Pipelines](#phase-1-local-development--data-pipelines)
- [Phase 2: Enterprise Orchestration for ML](#phase-2-enterprise-orchestration-for-ml)
- [Learning Path](#learning-path)
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
| Kubernetes | Intermediate |
| AWS EKS | Working knowledge |
| Python | Basic (read and run scripts) |

No ML experience needed. That is what this repo teaches.

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

**Goal:** Replace local, manual ML workflows with production-grade orchestration. Versioned data, automated pipelines, experiment tracking, and scalable training.

| Step | Title | Guide |
|------|-------|-------|
| 1 | Data Versioning Fundamentals  | [Read the Guide](https://newsletter.devopscube.com/p/mlops-data-drift-model-decay-and-dataset-versioning) |
| 2 | Data Version Control (DVC) with AWS S3 | [Read the Guide](https://newsletter.devopscube.com/p/mlops-versioning-data-with-dvc)|
| 3 | Data Versioning using Airflow on Kubernetes | [Read The Guide](https://newsletter.devopscube.com/p/mlops-airflow-dvc-pipeline)|
| 4 | Feature Store Fundamentals Explained | [Read The Guide](https://newsletter.devopscube.com/p/mlops-feature-store) |
| 5 | Hands-on Feature Store with Feast on Kubernetes | [Read The Guide](https://devopscube.com/setup-feature-store-feast-on-kubernetes/) |
| 4 | Kubeflow Explained for MLOps | 🔜 Coming Next |

Code: `phase-2-enterprise-setup/`

---

## Learning Path

| Phase | Track | Title | Status |
|-------|-------|-------|--------|
| 1 | 🤖 Traditional ML | [Local Dev & Pipelines](#phase-1-local-development--data-pipelines) | ✅ Done |
| 1 | 🤖 Traditional ML | K8s Deploy & Model Serving | ✅ Done |
| 3 | 🤖 Traditional ML | Enterprise Orchestration | 🔄 In Progress |
| 4 | 🤖 Traditional ML | Monitor & Observe | 🔜 Planned |
| 5 | 🧠 Foundational Models | Foundational Models | 🔜 Planned |
| 6 | 🧠 Foundational Models | LLM Serving & Scaling | 🔜 Planned |
| 7 | ⚙️ LLM-Powered DevOps | LLM-Powered DevOps | 🔜 Planned |
| 8 | ⚙️ LLM-Powered DevOps | Emerging AI Ops | 🔜 Planned |

---

## Tech Stack

Here is the tech stack you will be using in this setup.

| Category | Tools |
|----------|-------|
| Data Pipeline | Python, Airflow |
| Model Training | scikit-learn |
| API / Serving | FastAPI, Flask, Docker, KServe |
| ML Orchestration | Kubeflow, MLflow Pipelines |
| Monitoring | Prometheus, Grafana, Evidently AI |
| Infrastructure | Kubernetes, Helm, GitHub Actions |

---

## Recommended Reading

- [Google MLOps Whitepaper](https://cloud.google.com/resources/mlops-whitepaper)
- [Volkswagen's End-to-End MLOps Platform on AWS](https://aws.amazon.com/solutions/case-studies/volkswagen-mlops/)

## Certifications

- [AWS Certified Machine Learning Engineer - Associate](https://aws.amazon.com/certification/certified-machine-learning-engineer-associate/)
- [Nvidia AI Infrastructure and Operations](https://www.nvidia.com/en-us/training/)

---
## MLOps Tools

- [Ray](https://github.com/ray-project/ray): Open-source distributed computing framework For Python & AI Workloads
- [rtk](https://github.com/rtk-ai/rtk): High-performance CLI proxy that reduces LLM token consumption.
- [CML](https://github.com/iterative/cml): CI/CD for Machine Learning Projects

## License

Dual licensed:

- **Code** (scripts, configs, manifests) — Apache 2.0
- **Content** (README, guides, docs) — All Rights Reserved

For commercial licensing: contact@devopscube.com
