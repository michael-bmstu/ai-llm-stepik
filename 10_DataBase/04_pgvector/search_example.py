import asyncpg
import asyncio
import os
from dotenv import load_dotenv
from langchain.embeddings import init_embeddings
from pgvector.asyncpg import register_vector
from pprint import pprint

load_dotenv()

DATABASE_DSN = f"{os.getenv("DB_DSN_PREF")}/vector_db"

# $ - placeholders
GET_NEAREST_DATA_SQL = """
SELECT id, embedding <=> $1 AS distance, text
FROM items
ORDER BY distance
LIMIT $2;
"""

embeddings = init_embeddings(model="mistralai:mistral-embed", api_key=os.getenv("MISTRAL_KEY"))
query_vector = embeddings.embed_query("Что такое большая языковая модель?")