import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_DSN = f"{os.getenv("DB_DSN_PREF")}/test_db"

async def init_database():
    conn: asyncpg.Connection = await asyncpg.connect(DATABASE_DSN)
    try:
        await conn.execute("""
            CREATE TYPE transaction_type AS ENUM (
                'u2u', 'top-up', 'llm'
            );
        """)
        await conn.execute("""
            DROP TABLE IF EXISTS transactions;
            CREATE TABLE IF NOT EXISTS transactions (
                id UUID PRIMARY KEY,
                user_id UUID NOT NULL,
                transaction_type transaction_type NOT NULL,
                value INTEGER NOT NULL,
                metadata JSONB NOT NULL,
                tags TEXT[] DEFAULT array[]::TEXT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    asyncio.run(init_database())