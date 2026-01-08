from typing import Annotated
import asyncpg
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
import os
from dotenv import load_dotenv
import logging


load_dotenv()
DATABASE_DSN = f"{os.getenv("DB_DSN_PREF")}/test_db"
pool = None

async def db_connection():
    async with pool.acquire() as conn:
        yield conn


@asynccontextmanager
async def lifespan(app: FastAPI):
    global pool
    pool = await asyncpg.create_pool(DATABASE_DSN, min_size=3, max_size=9)
    # logging.debug("Pool was created")
    yield
    await pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/test")
async def test(conn: Annotated[asyncpg.Connection, Depends(db_connection)]):
    result = await conn.fetchval("SELECT 9999999+100000")
    return {"result": result}

"""
run command
uv run fastapi run 10_DataBase/03_transactions/fastapi_pool.py
"""