import uuid
from qdrant_client import QdrantClient
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import Distance, VectorParams
from langchain.embeddings import init_embeddings
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
import uuid
import pandas as pd
import time
import os
from dotenv import load_dotenv

load_dotenv()

COLLECTION_NAME = "spams"
# DATASET_PATH = "10_DataBase/05_qdrant/spams.csv"
DATASET_PATH = "spams.csv"

df = pd.read_csv(DATASET_PATH)

embeddings = init_embeddings(model="mistralai:mistral-embed", api_key=os.getenv("MISTRAL_KEY"))
texts = df['Message'].to_list()
spam_facts = df["Category"].map(lambda cat: cat == "spam").to_list()
docs = [Document(page_content=text, metadata={"is_spam": spam}, id=str(uuid.uuid4())) for text, spam in zip(texts, spam_facts)]

# client = QdrantClient(url="http://localhost:6333")
client = QdrantClient(url="http://qdrant:6333")
try:
    client.create_collection(COLLECTION_NAME, vectors_config=VectorParams(size=1024, distance=Distance.COSINE),)
except UnexpectedResponse:
    client.delete_collection(COLLECTION_NAME)
    client.create_collection(COLLECTION_NAME, vectors_config=VectorParams(size=1024, distance=Distance.COSINE),)

qdrant = QdrantVectorStore(client, COLLECTION_NAME, embeddings)
print("Collections created")

batch = 32
timeout = 1.5
for i in range(0, len(docs), batch): # processing by batch
    cur_timeout = timeout
    while True:
        try:
            res = qdrant.add_documents(docs[i:i + batch]) # return ids
            break
        except Exception as e:
            print(e)
            cur_timeout *= 3 # increace timeout to fix error
            print(f"incrase timeout to {cur_timeout}")
            time.sleep(cur_timeout)
    time.sleep(cur_timeout)
    print("processed", min(i + batch, len(docs)), "samples")

print("Data was vectorized")