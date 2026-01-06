from langchain_community.document_loaders import PyPDFLoader
from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableParallel, RunnableLambda, RunnableConfig
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document
import chainlit as cl
import os
from dotenv import load_dotenv
import time

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



@cl.on_chat_start
async def add_data_base():
    files = None
    while not files:
        user_file = cl.AskFileMessage(
            content="Please, upload the file",
            accept=["application/pdf"],
            max_size_mb=20,
            timeout=60,
        )
        files = await user_file.send()
        if not files:
            await user_file.remove()

    file = files[0]
    process_msg = cl.Message(content=f"Processing file {file.name}")
    await process_msg.send()

    loader = PyPDFLoader(file.path)
    chunks = loader.load_and_split(RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200))
    process_msg.content = f"File was processed and splited by {len(chunks)} chunks"
    await process_msg.update()
    
    vectorstore = InMemoryVectorStore(embeddings)
    async def add_documents_with_timeout(docs, timeout:float=2, batch:int=16):
        for i in range(0, len(docs), batch):
            cur_timeout = timeout
            while True:
                try:
                    vectorstore.add_documents(docs[i:i + batch])
                    break
                except:
                    cur_timeout *= 3
                    time.sleep(cur_timeout)
            time.sleep(cur_timeout)
            process_msg.content = f"Processed {min(i + batch, len(docs))} chunks"
            await process_msg.update()
    await add_documents_with_timeout(chunks)
    process_msg.content = f"Vector store from chunks was created"
    await process_msg.update()


    retriver = vectorstore.as_retriever(search_kwargs={"k": 3})
    format_context = RunnableLambda(lambda docs: "\n\n".join(d.page_content for d in docs))\
    .with_config(config=RunnableConfig(run_name="format documents"))

    chain = RunnableParallel(context=retriver | format_context, question=lambda q: q
        ) | RunnableParallel(
            answer=prompt | llm | StrOutputParser(), chunks=lambda d: d["context"], prompt=prompt
        )
    cl.user_session.set("chain", chain)
    cl.sleep(2)
    process_msg.content = "Processing is complete, the chatbot is ready to work"
    await process_msg.update()

@cl.on_message
async def main(message: cl.Message):
    chain: Runnable = cl.user_session.get("chain")
    res = await chain.ainvoke(message.content)
    context_chunks = [cl.Text(content=chunk, name=f"Context fragment {i}", display="inline")
                       for i, chunk in enumerate(res["chunks"].split("\n\n"))]
    await cl.Message(content=res["answer"], elements=context_chunks).send()

"""
chainlit run 07_chainlit/02_rag_ui.py
"""