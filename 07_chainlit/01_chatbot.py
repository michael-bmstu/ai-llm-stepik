import chainlit as cl
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.history import RunnableWithMessageHistory, BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
import os
from dotenv import load_dotenv

load_dotenv()

DOMAIN = "biology"
session_store = dict()

def get_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

messages = [
    ("system", "You are an expert in {domain}. Your task is answer the question as short as possible"),
    ("placeholder", "{history}"),
    ("human", "{question}"),
]

prompt = ChatPromptTemplate(messages)
llm = init_chat_model(model="mistral-large-latest", api_key=os.getenv("MISTRAL_KEY"))
chain = RunnableWithMessageHistory(
   prompt | llm, get_session_history=get_history,
   input_messages_key="question", history_messages_key="history",
) | StrOutputParser()

@cl.on_message
async def handle_message(message: cl.Message):
    user_session = cl.user_session.get("id")
    question = message.content
    msg = cl.Message(content="")
    async for chunk in chain.astream(
        {"domain": DOMAIN, "question": question, "history": messages}, 
        config=RunnableConfig(configurable={"session_id": user_session})
    ):
        await msg.stream_token(chunk)
    await msg.send()

# TODO
"""
chat profile
actions
app settings (temperature, model)
hello message
"""

"""
chainlit run 07_chainlit/01_chatbot.py
"""