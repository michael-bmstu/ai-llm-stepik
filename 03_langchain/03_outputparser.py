from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel, Field
from typing import Literal, Optional
from config import mistral_params

llm = ChatMistralAI(
    model="mistral-large-latest",
    temperature=0.1,
    api_key=mistral_params["api_key"],
)

class Computer(BaseModel):
    manufacturer: str = Field(description="Name of manufacturer")
    model: Optional[str] = Field(description="Model name", default=None)
    ram: int = Field(description="RAM size in GB", default=16)
    hard: int = Field(description="Size of hard memodry in GB", default=512)
    type_memory: Literal["ssd", "hdd"] = Field(description="Type of memory", default="ssd")

print("PydanticOutputParser")
parser = PydanticOutputParser(pydantic_object=Computer)
print("instructions:", parser.get_format_instructions())
messages_1 = [
    ("system", "Handle user query.\n{format}"),
    ("human", "{user_query}"),
]
prompt_template = ChatPromptTemplate(messages_1)
prompt_value = prompt_template.invoke(
    {
        "format": parser.get_format_instructions(),
        "user_query": "Ноутбук MSI модели 14-bm-422 8/512 SSD",
    }
)
parsed = llm.invoke(prompt_value)
print("Row parsed (by llm):", parsed.content)
print()
print("Parsed:", parser.invoke(parsed))
print()

print("Structed output")
messages_2 = [
    ("system", "Handle the user query"),
    ("human", "Ноутбук MSI модели 14-bm-422 8/512 SSD")
]

prepared_llm = llm.with_structured_output(Computer)
answer = prepared_llm.invoke(messages_2)
print(answer)