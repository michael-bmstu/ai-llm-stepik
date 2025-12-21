import os
from dotenv import load_dotenv
from typing_extensions import TypedDict, Annotated
from collections.abc import Sequence
from pydantic import BaseModel, Field
from datetime import datetime

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

load_dotenv()

# State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    number_of_steps: int

# Tools
@tool(return_direct=True)
def get_this_year_tool() -> int:
    """Получить текущий год"""
    return datetime.now().year

class WikiInput(BaseModel):
    query: str = Field(description="Запрос для поиска в Википедия")

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper(lang="ru"))

@tool(return_direct=True, args_schema=WikiInput)
def search_using_wikipedia(query: str) -> str:
    """Позволяет искать что-то в Википедия"""
    return wikipedia.run({"query": query})

tools = [search_using_wikipedia, get_this_year_tool]
tool2name = {tool.name: tool for tool in tools}

# Nodes
def call_tool(state: AgentState):
    output = []
    for tool_call in state["messages"][-1].tool_calls:
        res = tool2name[tool_call['name']].invoke(tool_call['args'])
        output.append(ToolMessage(
            content=res,
            name=tool_call['name'],
            tool_call_id=tool_call['id']
        ))
    return {"messages": output, "number_of_steps": state["number_of_steps"] + 1}

def call_model(state: AgentState, config: RunnableConfig):
    model = init_chat_model(
        model="mistral-large-latest",
        api_key=os.getenv("MISTRAL_KEY"),
        temperature=0)
    model = model.bind_tools(tools) # !!!
    resp = model.invoke(state["messages"], config)
    return {"messages": [resp], "number_of_steps": state["number_of_steps"] + 1}

# Edges
def is_continue(state: AgentState):
    last = state["messages"][-1]
    if not last.tool_calls:
        return "end"
    return "continue"

# Graph
builder = StateGraph(AgentState)
builder.add_node("llm", call_model)
builder.add_node("tool", call_tool)

builder.add_edge(START, "llm")
builder.add_conditional_edges("llm", is_continue, {"continue": "tool", "end": END})
builder.add_edge("tool", "llm")

graph = builder.compile()

# Visual
with open("04_tools_agents/graph_agent.png", "wb") as f:
    f.write(graph.get_graph().draw_mermaid_png())

inputs = {"messages": [("user", 
                        "Сколько лет прошло с появления передачи Поле чудес в эфире? Кто её ведущий сейчас? Сколько ему лет?"
                        # "Какой сейчас год?",
                        )],
                          "number_of_steps": 0}
state = graph.invoke(inputs)

for msg in state["messages"]:
    msg.pretty_print()
    print("=" * 80 + "\n")