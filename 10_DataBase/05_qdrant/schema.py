from pydantic import BaseModel, Field

class Doc(BaseModel):
    id: int
    text: str
    is_spam: bool

class QueryRequest(BaseModel):
    query: str = Field(examples=["Win a VIP weekend getaway! Text HOLIDAY to 63355 for your chance to claim (£2/msg)"])
    limit: int = Field(examples=[5])
    threshold: float = Field(default=0.5)

class QueryResponse(BaseModel):
    sim_documents: list[Doc]
    is_spam: bool
    probability: float