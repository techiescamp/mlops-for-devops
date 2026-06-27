import os
import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_aws import ChatBedrockConverse
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory

# load env variables
load_dotenv()

AWS_REGION = os.environ["AWS_REGION"]
BEDROCK_LLM_MODEL = os.environ["BEDROCK_LLM_MODEL"]

VECTOR_DB_URL = os.environ["VECTOR_DB_URL"]
HOST = os.environ.get("MAIN_HOST", "localhost")
PORT = int(os.environ.get("MAIN_PORT", "8000"))


# Bedrock LLM configuration
llm = ChatBedrockConverse(
    region_name=AWS_REGION,
    model=BEDROCK_LLM_MODEL
)

# fastapi app
app = FastAPI()

# enable cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# for memory intialization
history = ChatMessageHistory()

memory = ConversationBufferMemory(
    chat_memory=history,
    memory_key='chat_history',
    k=5,
    return_messages=True,
    output_key="answer"
)

class QueryRequest(BaseModel):
    query: str
    isEvaluate: bool = True # whether to compute runtime evaluation metrics

@app.post("/query")
async def query_rag(request: QueryRequest):
    print('🧑🏻‍🦱 query: ', request.query)
    try:
        query = request.query

        # search the docs based on query in vector-db 
        search_response = requests.post(f"{VECTOR_DB_URL}/search", json={"query": query})

        if search_response.status_code != 200:
            raise HTTPException(status_code=502, detail=f"Vector DB Error: {search_response.text}")

        search_results = search_response.json()
        print("Retrieved Docs: ", search_results)

        # combine doc as context 
        context = "\n\n".join(doc['content'] for doc in search_results)

        prompt_template = ChatPromptTemplate.from_template(
            """
            You are a helpful AI assistant that explains concepts to beginners with examples and code. 
            Use the provided context and chat history to answer the question. Avoid spelling mistakes.
            If the context does NOT help answer the question, clearly mention that it's "out of context" and prefix your answer with a 🌟 emoji.

            Chat History: {chat_history}
            Context: {context}
            Question: {question}
            Answer: 
            """
        )

        chain = (
            {
                "context": lambda x: context,
                "question": RunnablePassthrough(),
                "chat_history": lambda x: memory.load_memory_variables({"question": x})['chat_history'] 
            }
            | prompt_template
            | llm
            | StrOutputParser()
        ) 

        result = chain.invoke(query)

        memory.save_context({"question": query}, {"answer": result})

        return {
            "answer": result,
            "sources": [
                doc['metadata']['source'] 
                for doc in search_results if 'metadata' in doc and 'source' in doc['metadata']
            ],
        }

    except Exception as e:
        print(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
