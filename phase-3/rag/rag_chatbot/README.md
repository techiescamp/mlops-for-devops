
## RAG powered chatbot by webscraping the Kubernetes documents

**RAG** - **Retrieval Augmented Generation** is a workflow that's simplifies the use of generating content by taking one's own knowledge base as reference. In fine-tuning, we have to store large content of data in the model, which can be resource-intensive and time-consuming, RAG streamlines the process by retrieving relevant information from a knowledge base dynamically and combining it with a language model to generate accurate, context-specific responses without the need for extensive retraining.


## Folder Structure
-----------------------------------------------------------------------------------

```bash
mlops
|__ frontend/
|__ main_backend/
  |__ main.py
  |__ /*
|__ sync_backend/
  |__ index.py
  |__ /*
|__ vector_store
  |__ index.py
  |__ /*
|__ requirements.txt
|__ .env
|__ README.md

```

## Getting Started
-----------------------------------------------------------------------------
To set up and run the project, follow these steps:

**Prerequisites**
- Python 3.10+
- Node for frontend v 22.14.0
- Install dependencies: `pip install -r requirements.txt`
- Azure OpenAI API credentials (set in a .env file)
- Markdown files in the docs/ directory

## Setup files
### 1. Clone the repository

```bash
git clone https://github.com/techiescamp/mlops.git
cd rag_chatbot_k8
```

### 2. Create Virtual Environment

```bash
python -m venv venv

venv/Scripts/activate (for windows)
source ./venv/Scripts/activate (for bash)
```

### 3. Install required libraries

```bash
pip install -r requirements.txt
```

### 4. Vector Store DB Setup

Run the script

```bash
cd vector_store
python index.py
```

### Sync Backend Setup

Run the script

```bash
cd sync_backend
python index.py
```

### Main Backend Setup

Run the script

```bash
cd main_backend
python main.py
```

### For Frontend Setup


```bash
cd frontend

npm install

npm start
```


### Why Use This Chatbot?
----------------------------------
- **Accurate Answers:** Retrieves and generates responses based on your project’s documentation.
- **Context-Aware:** Maintains conversation history for coherent interactions.
- **Efficient:** Uses vector search (FAISS) for fast document retrieval.
- **Cost-Conscious:** Tracks token usage and estimates costs for Azure OpenAI API calls.
- **Customizable:** Easily adapt the pipeline to other document formats or LLMs.


## Contribution
-----
We welcome contributions from the security community. Please read our [Contributing Guidelines](../CONTRIBUTION.md) before submitting pull requests.

## License
This project is licensed under the [MIT License](../LICENCE). See the  file for details


