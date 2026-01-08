import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def main():
    conn: asyncpg.Connection = await asyncpg.connect(host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"), 
                                                     user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), 
                                                     database="test_db")
    try:
        await conn.execute("TRUNCATE TABLE people")
        await conn.execute("CREATE TABLE IF NOT EXISTS people (id SERIAL PRIMARY KEY, name TEXT, age INTEGER)")
        await conn.execute("INSERT INTO people (name, age) VALUES ($1, $2)", 'Иван Иванов', 30)
        await conn.execute("INSERT INTO people (name, age) VALUES ($1, $2)", 'Иван Васин', 25)

        records = await conn.fetch("SELECT * FROM people")
        print(records)
        print(records[0]["name"], records[0]["age"])
    finally:
        if conn:
            await conn.close()

asyncio.run(main())    