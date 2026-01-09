from langchain.embeddings import init_embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from fastapi import FastAPI, Body, Depends
from typing import Annotated
import qdrant_client
from schema import Doc, QueryRequest, QueryResponse
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = "spams"
embeddings = init_embeddings(model="mistralai:mistral-embed", api_key=os.getenv("MISTRAL_KEY"))
app = FastAPI()

async def get_qdrant_db():
    client = qdrant_client.QdrantClient(url="http://localhost:6333")
    yield QdrantVectorStore(client, COLLECTION_NAME, embeddings)
QdrantDB = Annotated[QdrantVectorStore, Depends(get_qdrant_db)]


@app.post("/predict")
async def check_spam(qdrant_db: QdrantDB, data: QueryRequest = Body()) -> QueryResponse:
    res = await qdrant_db.asimilaryty_search(query=data.query, k=data.limit)
    docs = [Doc(id=doc.id, is_spam=doc.metadata['is_spam'], text=doc.page_content) for doc in res]
    prob = sum(doc.is_spam for doc in docs) / len(docs)
    return QueryResponse(sim_documents=docs, is_spam=prob > data.threshold, probability=prob)

"""
run command
fastapi run 10_DataBase/05_qdrant/spam_api.py
"""