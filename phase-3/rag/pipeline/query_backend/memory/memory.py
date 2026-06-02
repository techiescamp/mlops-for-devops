from langchain_classic.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage


def create_memory():
    return ConversationBufferMemory(
        chat_memory=ChatMessageHistory(),
        memory_key="chat_history",
        k=5,
        return_messages=True,
        output_key="answer"
    )


def get_chat_history(memory, query: str) -> list:
    chat_history = memory.load_memory_variables({"question": query})['chat_history']
    messages = []
    for m in chat_history:
        if isinstance(m, HumanMessage):
            messages.append({'role': 'user',      'content': [{'text': m.content}]})
        elif isinstance(m, AIMessage):
            messages.append({'role': 'assistant', 'content': [{'text': m.content}]})
    return messages


def save_to_memory(memory, query: str, answer: str):
    memory.save_context({'question': query}, {'answer': answer})
