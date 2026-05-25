# AWS RAG Chatbot with Bedrock & S3 Vector Store

<div align="center">
  <img src="https://img.shields.io/github/stars/devopscube/rag-aws.svg?style=for-the-badge" alt="GitHub Stars" />
  <img src="https://img.shields.io/github/forks/devopscube/rag-aws.svg?style=for-the-badge" alt="GitHub Forks" />
  <img src="https://img.shields.io/github/contributors/devopscube/rag-aws.svg?style=for-the-badge" alt="Contributors" />
  <img src="https://img.shields.io/github/last-commit/devopscube/rag-aws.svg?style=for-the-badge" alt="Last Commit" />
  <img src="https://img.shields.io/badge/python-3..12.x-blue?style=for-the-badge" alt="Python Version" />
</div>

<hr />

## Overview

A production-ready Retrieval-Augmented Generation (RAG) chatbot leveraging AWS Bedrock for LLMs and Amazon S3 Vector as a scalable vector store. This project enables enterprise-grade, context-aware conversational AI over your private documents.

## Table of Contents

1. [Problem Statement](#-problem-statement)
2. [Solution](#-solution)
3. [Features](#-features)
4. [Project Structure](#project-structure)
5. [Configuration](#-configuration)
6. [AWS Setup](#-aws-setup)
7. [Getting Started](#-getting-started)
    - [Clone the repo](#step-1-clone-the-repo)
    - [Setup .env file](#step-2-setup-env-file)
    - [Backend Setup](#step-3-backend-setup)  
    - [Run Microservice Backends](#step-4-run-following-microservices-backend)
    - [Setup Frontend](#step-5-setup-frontend)
8. [Future Customization](#-future-customization)
9. [Security & Privacy](#️-security--privacy)
10. [References](#-references)
11. [Contact](#-contact)
12. [Contributions](#-contributing)
13. [Licence](#-license)


## 🚩 Problem Statement
Organizations need secure, scalable, and accurate chatbots that can answer questions based on their own documents, not just public internet data. 

Existing solutions often:

- Struggle with up-to-date or proprietary knowledge
- Lack scalable, cost-effective vector storage
- Are hard to deploy in cloud-native environments

## 💡 Solution
This project provides a full-stack RAG chatbot that:

- Uses AWS Bedrock for powerful, managed LLMs
- Stores and retrieves document embeddings from S3 (object storage as a vector DB)
- Supports easy document ingestion, search, and chat
- Is cloud-native, modular, and ready for production



## ✨ Features

- **Retrieval-Augmented Generation (RAG)**: Combines LLMs with your own data
- **AWS Bedrock Integration**: 
Secure, scalable LLM access
- **S3 Vector Store**: Cost-effective, serverless vector storage
- **Document Sync & Indexing**: Easily add/update docs
- **Modern Frontend**: React-based chat UI
- **Kubernetes/Cloud Ready**: Modular backend for easy deployment


## Project Structure

```bash
backend/
  main-backend/         # Main API for chat and retrieval
  sync-backend/         # Document sync, embedding, and S3 vector management
  vector-store/         # Vector search and storage logic
  .env
  requirements.txt      # install libraries
frontend/               # React app for chat UI
README.md
```

## ⚙️ Configuration

- **AWS Credentials**: Set in .env or via environment variables
- **S3 Bucket**: Used for vector storage
- **Bedrock Model**: I choosed,
    - Ttian Text Embedding V2 model for embeddings
    - Nova Micro for LLM
- **Langchain**: For RAG components like `memory`, `text-splitting` and `document schemas`
- **boto3 library**: This AWS SDK for Python.
- **FastAPI**: For API Backend services


## 👩🏻‍💻 AWS Setup

1. **Create S3 Bucket**: Create an S3 bucket for storing vectors
2. **Configure IAM Permissions**: Ensure your AWS credentials have:
   - `s3:GetVectors`, `s3:PutVectors`, `s3:QueryVectors` permissions for your S3 bucket
   - `bedrock:InvokeModel` and `bedrock:converse` permission for the Titan embedding model
3. **Enable Bedrock Model Access**: Enable access to Amazon Titan Embeddings in AWS Bedrock console


## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Langchain for RAG usage.
- AWS account with Bedrock & S3 Vector access.
- (Optional) Docker & Kubernetes for deployment


### Step-1 Clone the repo

```bash
git clone https://github.com/SravyaCrunchOps/rag-aws.git
cd rag-aws
```

### Step-2 Setup `.env` file

```bash
K8_REPO_URL=<docs-repo-url>

AWS_REGION=<aws-region>
AWS_ACCOUNT_ID=<aws-account-id>

BEDROCK_LLM_MODEL=<amazon.llm-model:0>
BEDROCK_EMBEDDING_MODEL_ID=<amazon.embedding-model:0>

S3_VECTOR_BUCKET_NAME=<bucket-name>
S3_VECTOR_INDEX_NAME=<index-name>

S3_VECTOR_URL=arn:aws:s3vectors:<aws-region>:<aws-account-id>:bucket/<bucket-name>/index/<index-name>

MAIN_BACKEND_HOST=<host-address>
MAIN_BACKEND_PORT=<port-number>

VECTOR_DB_URL=<vector-store-url>
VECTOR_DB_HOST=<host-address>
VECTOR_DB_PORT=<port-number>
```

### Step-3 Backend Setup

Use virtual environment and install required libraries from `requirements.txt`

```bash
cd backend

python -m venv venv
venv/Scripts/activate    # for windows

pip install -r requirements.txt
```

### Step-4 Run Following Microservices Backend

#### 4.1. Sync-backend 

**Note**: Not a service API server. It runs only once to pull docs from GitHub. It is more like a cron-job that updates this backend once in a month to update new changes of docs.

```bash
python index.py
```

**Description**:

- Creates `temp-doc/` folder for pulling docs from GitHub. You can either delete or keep this folder.

- Load these docs to `k8-docs/` folder. This folder must be present for embedding process.

- Splits the docs into chunks to make process easier for embedding large documents.

- Then embedding process is starts by passing through batches to avoid throttling.


#### 2. Vector-store backend

```bash
uv run index.py

or

uvicorn index:app --reload --port 8002
```

Example: runs on port 8002. `http://localhost:8002`

**Description**:

- `/store` api endpoint:
    - Recieve docs in batches from `sync-backend` and starts embedding.

    - For embedding process used **`AWS Bedrock Titan Text Embedding V2`** model. 

    - Calls `S3 Vector Storage` to store these embeddings.

- `/search` API Endpoint:
    - Recieves query from `main-backend` and embed the query using `Titan Text Embedding V2`

    -  AWS S3 Vector calls function `query_vectors()` to search query and retrieves `top_k` (in this case 4) documents and send it to `main-backend`

    - Here used simple search - `Cosine similarity Search` which was set during AWS Vector Index configuration setup.

#### **Note**: 
Why did not use embedding model in `sync-backend` ?
To avoid repeated use/call of embedding model in two backends I want to use in only one backend service for both `embedding and searching`.


#### 3. Main-Backend 

```bash
uv run index.py

or

uvicorn index:app --reload --port 8000
```

Example: runs on port 8000. `http://localhost:8000`

**Description**:
- Recieves query from UI and send it to `vector-store` backend service for searching and retrieveing docs.

- The retrieved docs + query + chat-history combine together in `message` varaible and calls the LLM model.

- For LLM Model used **`AWS Bedrock Nova Micro`** model is which cheaper, produce accurate results and best for RAG like projects.


#### Step-5 Setup Frontend

```bash
# for development
npm install
npm start 

# for production
npm run build
node server.js

```

## 🧩 Future Customization

- Add new document loaders/parsers in `sync-backend/`
- Swap out vector store logic in `vector-store/` 
- Try out different LLM models in-place of AWS models.
- Customize chat UI components in `components/`.


## 🛡️ Security & Privacy
- All data stays in your AWS account
- No third-party data sharing
- Supports private, internal deployments


## 📚 References

- AWS Bedrock
- Amazon S3
- LangChain (if used)


## 📬 Contact
For questions or support, open an issue or contact the maintainers.


## 🤝 Contributing
Pull requests are welcome! See [CONTRIBUTIONS.md](CONTRIBUTIONS.md).


## 📄 License
This repo is under [MIT Licence](LICENCE) support.