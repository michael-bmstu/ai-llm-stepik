import aiofiles
import json
import os
from uuid import UUID
from .models import Book


DATA = "../books.json"

async def load_books() -> list[Book]:
    books = []
    if not os.path.exists(DATA):
        return books
    async with aiofiles.open(DATA, 'r', encoding='utf-8') as f:
        content = await f.read()
        raw_list = json.loads(content)
    for raw_data in raw_list:
        book_id = UUID(raw_data["id"])
        updated_raw_data = {**raw_data, "id": book_id}
        books.append(Book(**updated_raw_data))
    return books


async def save_books(books: list[Book]):
    data = [{**book.model_dump(exclude={"id"}), "id": str(book.id)} for book in books]
    async with aiofiles.open(DATA, 'w', encoding='utf-8') as f:
        content = json.dumps(data, indent=4)
        await f.write(content)