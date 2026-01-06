from langchain_community.document_loaders import PyPDFLoader
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
import chainlit as cl
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("MISTRAL_KEY")

prompt = ChatPromptTemplate([
    (
        "system",
        (
            "You are an assistant for QA. Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, just say that you don't know. Answer as short as possible. "
            "Context: {context} \n Question:"
        )
    ),
    ("human", "{question}")
])

llm = init_chat_model(model="mistral-large-latest", api_key=API_KEY)
embeddings = init_embeddings(model="mistralai:mistral-embed", api_key=API_KEY)