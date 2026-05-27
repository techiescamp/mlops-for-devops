import os
import requests
import uvicorn

import boto3
from botocore.config import Config

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_classic.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage

from dotenv import load_dotenv


load_dotenv()

# env constants
BEDROCK_LLM_MODEL = os.environ["BEDROCK_LLM_MODEL"]
AWS_REGION = os.environ["AWS_REGION"]

VECTOR_DB_URL = os.environ["VECTOR_DB_URL"]
HOST = os.environ["MAIN_BACKEND_HOST"]
PORT = int(os.environ["MAIN_BACKEND_PORT"])

# llm model
config = Config(
    connect_timeout=10,
    read_timeout=60,
    retries={'max_attempts': 3}
)
bedrock = boto3.client("bedrock-runtime", region_name=AWS_REGION, config=config)



# fast api
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

memory = ConversationBufferMemory(
    chat_memory=ChatMessageHistory(),
    memory_key="chat_history",
    k=5,
    return_messages=True,
    output_key="answer"
)

class QueryRequest(BaseModel):
    query: str
    isEvaluate: bool = True
    # filter: dict = None  # e.g., {"metadata.source": {"eq": "file.md"}}


@app.post("/query")
async def query_rag(request: QueryRequest):
    print(request)
    query = request.query
    print(query)

    search_payload = { "query": query }
    
    response = requests.post(f"{VECTOR_DB_URL}/search", json=search_payload)
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Vector DB Error: {response.text}")

    results = response.json()

    # build context by concatenating content
    context = "\n\n".join(doc["content"] for doc in results)

    # build source list
    source_list = [doc.get("metadata", {}).get("source") for doc in results]

    system_prompt = """
        You are a helpful AI assistant that explains concepts to beginners with examples and code. 
        If the context does NOT help answer the question, clearly mention that it's "out of context" 
    """

    messages = []
    # chat history
    chat_history = memory.load_memory_variables({"question": query})['chat_history']
    # print('chat-history: ', chat_history)
    # [HumanMessage(content='explain dns pod service in K8', additional_kwargs={}, response_metadata={}), 
    # AIMessage(content='Certainly! In Kubernetes, the concept of DNS ..', additional_kwargs={}, response_metadata={})]
    for m in chat_history:
        if isinstance(m, HumanMessage):
            messages.append({'role': 'user', 'content': [{'text': m.content}]})
        elif isinstance(m, AIMessage):
            messages.append({'role': 'assistant', 'content': [{'text': m.content}]})
    
    # print('msg-before-query: ', messages)
    
    messages.append({"role": "user", "content": [{'text': f"Context: {context}\nQuestion: {query}"}] })
    
    response = bedrock.converse(
        modelId=BEDROCK_LLM_MODEL,
        system=[{'text': system_prompt}],
        messages=messages,
        inferenceConfig={
            "maxTokens": 512,
            "temperature": 0.7
        }
    )
    output = response["output"]["message"]["content"][0]["text"]
    memory.save_context({'question': query}, {'answer': output})
    return {"answer": output, "source": source_list}
    # {
    # 'output': {
    #     'message': {
    #         'role': 'user'|'assistant',
    #         'content': [
    #             {
    #                 'text': 'string',
    #                 ....
    #             }
    #         ]
    #     }}
    # }

                    
@app.get("/health")
async def health_check():
    return {"status": "healthy"}



if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)                  
         
                        