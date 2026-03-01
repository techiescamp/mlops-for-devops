# MLOps for DevOps Engineers

A hands-on, project-based guide to Machine Learning Operations — built specifically for DevOps, Platform, and SRE engineers.

[![Code: Apache 2.0](https://img.shields.io/badge/Code-Apache%202.0-blue.svg)](licenses/LICENSE-CODE)
[![Content: All Rights Reserved](https://img.shields.io/badge/Content-All%20Rights%20Reserved-red.svg)](licenses/LICENSE-CONTENT)
[![GitHub Stars](https://img.shields.io/github/stars/techiescamp/mlops-for-devops?style=social)](https://github.com/techiescamp/mlops-for-devops)

> **No ML background required.** Every concept is explained through DevOps analogies you already understand.
> If you are completely new to the MLOPS concept, please read our [DevOps to MLOps](https://devopscube.com/devops-to-mlops/) guide first.

## Hit the Star! :star:

If you are planning to use this repo for reference, please hit the star. Thanks!

## Table of Contents

- [What Is This?](#what-is-this)
- [Use Case](#use-case)
- [Prerequisites](#prerequisites)
- [Learning Path](#learning-path)
  - [Phase 1: Local Development & Data Pipelines](#phase-1-local-development--data-pipelines)
  - Phase 2 — Deployment & Model Serving *(coming soon)*
  - Phase 3 — Enterprise Orchestration *(coming soon)*
  - Phase 4 — Model Observability & Monitoring *(coming soon)*
  - Phase 5 — Foundational Models *(coming soon)*
- [Tech Stack](#tech-stack)
- [Recommended Reading](#recommended-reading)
- [Contributing](#contributing)
- [License](#license)

## What Is This?

Most MLOps resources are written for data scientists learning 
infrastructure. This repo flips that. It is written for **DevOps 
engineers learning ML operations**.

You do not need to become a data scientist. But just like understanding 
how a Java application is built makes you a better DevOps engineer, 
understanding how an ML model is built, trained, and served makes you 
effective at operating ML workloads in production.

Here is what we build, end to end:

**🤖 Traditional ML**
- Train and evaluate a real employee attrition prediction model locally
- Package and serve the model as an API on Kubernetes
- Automate the full ML pipeline with Kubeflow and MLflow
- Monitor model performance and detect drift in production

**🧠 Foundational Models**
- Serve large language models in production using vLLM, TGI, and Ollama
- Handle LLM hosting challenges, scaling, token optimization, cost
- Learn how enterprises solve these problems in real projects

**⚙️ LLM-Powered DevOps**
- Monitor Kubernetes clusters using LLMs
- Build internal chatbots, RAG pipelines, and agents
- Everything runs on Kubernetes, Docker, and tools you already use.

AI is moving fast. As new tools and techniques emerge that are relevant 
for DevOps, SRE, and Platform Engineering, we will cover them here. 

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

## Learning Path

```
Phase 1          Phase 2          Phase 3          Phase 4          Phase 5
─────────        ─────────        ─────────        ─────────        ─────────
 Local Dev   ──▶  Deploy &   ──▶  Enterprise  ──▶  Monitor &  ──▶  Foundation
 & Pipelines      Model Serve      Orchestration     Observe          Models
```

### Phase 1: Local Development & Data Pipelines

**Goal:** Build the ML foundation on your local machine.

| Step | Task | Documentation |
|------|-------|------------|
| Step 1 | Project Dataset Pipeline Explained | [Read the Guide](https://newsletter.devopscube.com/p/building-a-dataset-pipeline) |
| Step 2 | Data Preparation Stages (hands-on) | [Read the Guide](https://newsletter.devopscube.com/p/mlops-data-preparation) |
| Step 3 | Training & Building the Prediction Model (hands on) | [Read the Guide](https://newsletter.devopscube.com/p/mlops-training-the-model) |

**Code:** [`phase-1-local-dev/`](phase-1-local-dev/)
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
- [Volkswagen’s End-to-End MLOps Platform on AWS](https://aws.amazon.com/blogs/industries/how-volkswagen-and-aws-built-end-end-mlops-for-digital-production-platform/)

## Certifications

1. [AWS Certified Machine Learning Engineer - Associate](https://aws.amazon.com/certification/certified-machine-learning-engineer-associate/)
2. [Nvidia AI Infrastructure and Operations](https://www.nvidia.com/en-us/learn/certification/ai-infrastructure-operations-associate/)


## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This repository uses a dual license:

- **Code** (Python scripts, configs, manifests) — [Apache 2.0](licenses/LICENSE-CODE). Free to use with attribution.
- **Content** (README, guides, documentation) — [All Rights Reserved](licenses/LICENSE-CONTENT). No copying or redistribution permitted.

For commercial licensing: contact@devopscube.com
