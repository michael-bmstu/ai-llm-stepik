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

# Model init
llm = init_chat_model(model="mistral-large-latest", api_key=API_KEY)
embeddings = init_embeddings(model="mistralai:mistral-embed", api_key=API_KEY)

@cl.on_chat_start
async def add_data_base():
    files = None
    cur_user = cl.user_session.get("user")
    while not files:
        user_file = cl.AskFileMessage( # get file from user in dialogue
            content=f"{cur_user.display_name}, upload the file, please",
            accept=["application/pdf"],
            max_size_mb=20,
            timeout=60,
        )
        files = await user_file.send()
        if not files:
            await user_file.remove() # keep waiting

    file = files[0]
    # create info message
    process_msg = cl.Message(content=f"Processing file {file.name}")
    await process_msg.send()

    loader = PyPDFLoader(file.path)
    chunks = loader.load_and_split(RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=200))
    process_msg.content = f"File was processed and splited by {len(chunks)} chunks"
    await process_msg.update()
    
    vectorstore = InMemoryVectorStore(embeddings)
    # get timeout when processing many chunks to avoid blocking free mistralai api
    async def add_documents_with_timeout(docs, timeout:float=2, batch:int=16):
        for i in range(0, len(docs), batch): # processing by batch
            cur_timeout = timeout
            while True:
                try:
                    vectorstore.add_documents(docs[i:i + batch])
                    break
                except:
                    cur_timeout *= 3 # increace timeout to fix error
                    time.sleep(cur_timeout)
            time.sleep(cur_timeout)
            process_msg.content = f"Processed {min(i + batch, len(docs))} chunks"
            await process_msg.update()
        
    await add_documents_with_timeout(chunks)
    process_msg.content = f"Vector store from chunks was created"
    await process_msg.update()

    retriver = vectorstore.as_retriever(search_kwargs={"k": 3})
    # Concat retrived files
    format_context = RunnableLambda(lambda docs: "\n\n".join(d.page_content for d in docs))\
    .with_config(config=RunnableConfig(run_name="format documents"))
    # chain with retrive, concat, answer 
    chain = RunnableParallel(context=retriver | format_context, question=lambda q: q
        ) | RunnableParallel(
            answer=prompt | llm | StrOutputParser(), chunks=lambda d: d["context"], prompt=prompt
        )
    cl.user_session.set("chain", chain)
    cl.sleep(2) # avoid blocking free mistralai api
    process_msg.content = "Processing is complete, the chatbot is ready to work"
    await process_msg.update()

@cl.on_message
async def main(message: cl.Message):
    chain: Runnable = cl.user_session.get("chain") # get chain with database for current user
    res = await chain.ainvoke(message.content)
    # add context documents to answer to improve interpretability
    context_chunks = [cl.Text(content=chunk, name=f"Context fragment {i}", display="inline")
                       for i, chunk in enumerate(res["chunks"].split("\n\n"))]
    await cl.Message(content=res["answer"], elements=context_chunks).send()

users = [ # allowed users
    cl.User(identifier="1", display_name="Admin", metadata={"username": "admin", "password": "admin"}),
    cl.User(identifier="2", display_name="Mihail", metadata={"username": "miha", "password": "solov"}),
    cl.User(identifier="3", display_name="Dan", metadata={"username": "dan", "password": "ultra"}),
]

@cl.password_auth_callback # auth function
async def get_user(username: str, password: str):
    for user in users:
        if username == user.metadata["username"] and password == user.metadata["password"]:
            return user
    return None


"""
run command
chainlit run 07_chainlit/02_rag_ui.py
"""