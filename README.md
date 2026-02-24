# MLOps for DevOps Engineers

A hands-on, project-based guide to Machine Learning Operations — built specifically for DevOps, Platform, and SRE engineers.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/techiescamp/mlops-for-devops?style=social)](https://github.com/techiescamp/mlops-for-devops)

> **No ML background required.** Every concept is explained through DevOps analogies you already understand.

## Table of Contents

- [What Is This?](#what-is-this)
- [Use Case](#use-case)
- [Prerequisites](#prerequisites)
- [Learning Path](#learning-path)
  - [Phase 1 — Local Development \& Data Pipelines](#phase-1--local-development--data-pipelines)
  - Phase 2 — Deployment \& Model Serving
  - Phase 3 — Enterprise Orchestration
  - Phase 4 — Model Observability \& Monitoring
  - Phase 5 — Foundational Models
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

## Learning Path

```
Phase 1          Phase 2          Phase 3          Phase 4          Phase 5
─────────        ─────────        ─────────        ─────────        ─────────
 Local Dev   ──▶  Deploy &   ──▶  Enterprise  ──▶  Monitor &  ──▶  Foundation
 & Pipelines      Model Serve      Orchestration     Observe          Models
```

### Phase 1 — Local Development & Data Pipelines

**Goal:** Build the ML foundation on your local machine.

| Step | Task | Documentation |
|------|-------|------------|
| Step 1 | Project Dataset Pipeline Explained | [Read the Guide](https://newsletter.devopscube.com/p/building-a-dataset-pipeline) |
| Step 2 | Data Preparation Stages (hands-on) | [Read the Guide](https://newsletter.devopscube.com/p/mlops-data-preparation) |
| Step 3 | Training & Building the Prediction Model (hands on) | Coming Saturday |

**Code:** [`phase-1-local-dev/`](phase-1-local-dev/) · **Guide:** [`phase-1-local-dev/README.md`](phase-1-local-dev/README.md)

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
- [DevOps to MLOps — DevOpsCube](https://devopscube.com/devops-to-mlops/)
- [Google MLOps Whitepaper](https://cloud.google.com/resources/mlops-whitepaper)

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT — see [LICENSE](LICENSE).
git