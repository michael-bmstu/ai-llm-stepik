from uuid import uuid4, UUID
from pydantic import BaseModel, Field


class BaseBook(BaseModel):
    name: str = Field(examples=["Дубровский"])
    author: str = Field(examples=["А. С. Пушкин"])
    year: str = Field(examples=["1843"])
    annotation: str = Field(examples=["Классический роман о любви и чести"])

class Book(BaseBook):
    id: UUID = Field(examples=[uuid4()])

class CreateBook(BaseBook):
    pass

class UpdateBook(BaseBook):
    pass

class SuccessMessage(BaseModel):
    message: str = Field(examples=["Операция выполнена"])