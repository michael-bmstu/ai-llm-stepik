# llm chat
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
# docs
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_mistralai import MistralAIEmbeddings
# from langchain_huggingface import HuggingFaceEmbeddings
# chain
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableConfig
# trace
from openinference.instrumentation.langchain import LangChainInstrumentor
from phoenix.otel import register
# .env vars
from dotenv import load_dotenv
import os

import time

load_dotenv()

tracer = register(project_name="trace-example", endpoint="http://localhost:6006/v1/traces")
LangChainInstrumentor().instrument(tracer_provider=tracer)

loader = PyPDFLoader("06_debugging_arize_phoenix\paper.pdf")
pages = loader.load()[:5]
full_text = "\n".join(page.page_content for page in pages)
splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=100, add_start_index=True)
chunks = splitter.split_text(full_text)
docs = [Document(page_content=chunk, metadata={"source": "paper.pdf"}) for chunk in chunks]

# embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-base")
embeddings = MistralAIEmbeddings(model="mistral-embed", api_key=os.getenv("MISTRAL_KEY"))

vectorstore = InMemoryVectorStore.from_documents(docs, embedding=embeddings)
retriver = vectorstore.as_retriever(search_kwargs={'k': 3})

llm = init_chat_model(model="mistral-medium-latest", api_key=os.getenv("MISTRAL_KEY"), temperature=0)
prompt = ChatPromptTemplate([
    ("system", (
        "You are an assistant for QA. Use the following pieces of retrieved context to answer the question. "
        "If you don't know the answer, just say that you don't know. Answer as short as possible. "
        "Context: {context}"
    )),
    ("human", "Question: {question}")
])

format_context = RunnableLambda(lambda docs: "\n\n".join(d.page_content for d in docs))\
    .with_config(config=RunnableConfig(run_name="format documents"))

chain = RunnableParallel(context=retriver | format_context, question=lambda d: d) | prompt | llm | StrOutputParser()

result = chain.invoke("What is attention?")
print(result)