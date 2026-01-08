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
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS transactions_1 (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                value INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
            INSERT INTO users(id, name, username, hashed_password)
            VALUES
                ('user-1', 'Nikita', 'nick', '3s24sd234a324s'),
                ('user-2', 'Daniel', 'dan', '3s24sd234a324s');
        """)
    finally:
        if conn:
            await conn.close()


if __name__ == "__main__":
    asyncio.run(init_database())