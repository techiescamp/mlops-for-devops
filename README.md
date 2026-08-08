# MLOps for DevOps Engineers

A hands-on, project-based guide to Machine Learning Operations built specifically for DevOps, Platform, and SRE engineers.

> No ML background required. Every concept is explained through DevOps analogies you already understand.

If you are completely new to MLOps, read our [DevOps to MLOps guide](https://devopscube.com/devops-to-mlops/) first.

---
🌟🌟 If you are planning to use this repo for learning MLOps, please hit the star. Thanks!🌟🌟

---
## Table of Contents

- [Who This Is For](#who-this-is-for)
- [What We Build](#what-we-build)
- [Prerequisites](#prerequisites)
- [Tech Stack](#tech-stack)
- [Phase 1: Local Dev & Pipelines](#phase-1-local-development--data-pipelines)
- [Phase 2: Enterprise Orchestration for ML](#phase-2-enterprise-orchestration-for-ml)
- [Recommended MLOps Reading](#recommended-reading)
---

## Who This Is For

Most MLOps resources are written for data scientists learning infrastructure. This repo flips that.

**You do not need to become a data scientist**. But just like understanding how a Java application is built makes you a better DevOps engineer, understanding how an ML model is built, trained, and served makes you effective at operating ML workloads in production.

---

## What We Build

We will start with the basics of building and training a classic ML model, then work our way up to production-ready MLOps.

Just like a DevOps engineer doesn't write the application but understands how it is built and deployed, an MLOps engineer doesn't need to be a data scientist. Understanding the ML workflow helps you build, automate, deploy, and troubleshoot ML systems effectively.

Everything in this roadmap **runs on Kubernetes and Docker**, and tools you will use in real-world MLOps platforms.

---
## Tech Stack

Here is the tech stack you will be using in this setup.

| Category | Tools |
|----------|-------|
| Data Pipeline | Python, Airflow |
| Model Training | scikit-learn |
| API / Serving | FastAPI, Flask, Docker, KServe |
| ML Orchestration | Kubeflow, MLflow Pipelines |
| Monitoring | Evidently AI |
| Infrastructure | Kubernetes, Helm |

---

## Phase 1: Local Development & Data Pipelines (Start Here)

**Goal:** Build the required ML foundation by building an Employee attrition prediction model from your local systems.

**Use case throughout:** Employee attrition prediction for a large organisation (~500,000 employees). One problem, end-to-end. Keeps the focus on infrastructure and operations, not data science theory.

| Step | Title | Guide |
|------|-------|-------|
| 1 | Project Dataset Pipeline | [Read the Guide](https://newsletter.devopscube.com/p/building-a-dataset-pipeline) |
| 2 | Data Preparation Stages | [Read the Guide](https://newsletter.devopscube.com/p/mlops-data-preparation) |
| 3 | Training & Building the Prediction Model | [Read the Guide](https://newsletter.devopscube.com/p/mlops-training-the-model) |
| 4 | From Model to Live API with KServe | [Read the Guide](https://newsletter.devopscube.com/p/deploying-model-kserve) |

Code: `phase-1-local-dev/`

## Phase 2: Enterprise Orchestration for ML

**Goal:** Replace local and manual ML workflows with automated, scalable, and production-ready workflows.

This phase covers the following key MLOps areas:

- Data Versioned workflow
- Automated data pipelines
- Scalable training pipelines
- Experiment tracking
- Scalable model deployment
- Model monitoring

The following guides explain each of these areas using specific open-source MLOps tools.

| Step | Title | Guide |
|------|-------|-------|
| 1 | Data Versioning Fundamentals  | [Read the Guide](https://newsletter.devopscube.com/p/mlops-data-drift-model-decay-and-dataset-versioning) |
| 2 | Data Version Control (DVC) with AWS S3 | [Read the Guide](https://newsletter.devopscube.com/p/mlops-versioning-data-with-dvc)|
| 3 | Data Versioning using Airflow on Kubernetes | [Read The Guide](https://newsletter.devopscube.com/p/mlops-airflow-dvc-pipeline)|
| 4 | Feature Store Fundamentals Explained | [Read The Guide](https://newsletter.devopscube.com/p/mlops-feature-store) |
| 5 | Hands-on Feature Store with Feast on Kubernetes | [Read The Guide](https://devopscube.com/setup-feature-store-feast-on-kubernetes/) |
| 6 | Kubeflow Explained for MLOps | [Read The Guide](https://newsletter.devopscube.com/p/kubeflow-pipelines)  |
| 7 | Hands-on Kubeflow on Kubernetes | [Read The Guide](https://devopscube.com/setup-kubeflow-pipelines-kubernetes/) |
| 8 | Kubeflow Trainer Explained (Hands-on) | [Read the Guide](https://newsletter.devopscube.com/p/kubeflow-trainer) |
| 9 | MLflow: A Practical Guide to Experiment Tracking | [Read the Guide](https://newsletter.devopscube.com/p/mlfow) |
| 10| KServe for MLOps: A Practical Guide |[Read the Guide](https://newsletter.devopscube.com/p/kserve)|
| 11| Model Monitoring Explained | [Read the Guide](https://newsletter.devopscube.com/p/model-monitoring)| 
| 12| Model Monitoring - Hands On | [Read the Guide](https://devopscube.com/evidently-ai-on-kubernetes/)|

Code: `phase-2-enterprise-setup/`

## Capstone MLOps Project: End-to-End MLOps Projects on Kubernetes | 🔜 Planned |

In this capstone project, you'll build a production-style MLOps platform on Kubernetes by combining everything you've learned throughout this series.

By the end, you'll have built an enterprise-grade MLOps workflow that mirrors how modern organizations develop, train, track, and operate machine learning models on Kubernetes.

---

## Recommended Reading

- [Google MLOps Whitepaper](https://cloud.google.com/resources/mlops-whitepaper)
- [Volkswagen's End-to-End MLOps Platform on AWS](https://aws.amazon.com/solutions/case-studies/volkswagen-mlops/)
- [Discord Single-Node to Multi-GPU Clusters](https://discord.com/blog/from-single-node-to-multi-gpu-clusters-how-discord-made-distributed-compute-easy-for-ml-engineers)

## Certifications

- [AWS Certified Machine Learning Engineer - Associate](https://aws.amazon.com/certification/certified-machine-learning-engineer-associate/)
- [Nvidia AI Infrastructure and Operations](https://www.nvidia.com/en-us/training/)

---
## MLOps Tools

- [Ray](https://github.com/ray-project/ray): Open-source distributed computing framework For Python & AI Workloads
- [CML](https://github.com/iterative/cml): CI/CD for Machine Learning Projects
- [Dagster](https://github.com/dagster-io/dagster): Cloud-native data pipeline orchestrator
- [Kestra](https://github.com/kestra-io/kestra): Open-source orchestration platform for data, AI, and infrastructure workflows
- [Flyte](https://flyte.org/): AI orchestration in pure Python

## License

Dual licensed:

- **Code** (scripts, configs, manifests) — Apache 2.0
- **Content** (README, guides, docs) — All Rights Reserved

For commercial licensing: contact@devopscube.com
