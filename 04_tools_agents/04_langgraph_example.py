import random
from typing import Literal
import os
from dotenv import load_dotenv

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

load_dotenv()

# State
class State(TypedDict):
    query: str
    resolver: str
    answer: str

# Nodes
def choose_resolver(state: State) -> State:
    resolver = "support" if random.random() > 0.7 else "llm"
    state["resolver"] = resolver
    return state

def send_to_support(state: State) -> State:
    print(f"New message for support: {state['query']}")
    return state

def send_to_llm(state: State) -> State:
    messages = [
        ("system", "You are a friendly chatbot. Your task is answer the question as short as possible"),
        ("human", "{question}"),
    ]
    prompt = ChatPromptTemplate(messages)
    llm = init_chat_model(model="mistral-large-latest", api_key=os.getenv("MISTRAL_KEY"))
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"question": state['query']})
    state['answer'] = answer
    return state

def send_to_user(state: State) -> State:
    print(f"New message for user: {state['answer']}")
    return state

# Edge
def route_query(state: State) -> Literal['send_to_supprot', 'send_to_llm']:
    if state['resolver'] == "support":
        return "send_to_supprot"
    else:
        return "send_to_llm"
 
# Build graph #
builder = StateGraph(State)

# Nodes
builder.add_node("choose_resolver", choose_resolver)
builder.add_node("send_to_supprot", send_to_support)
builder.add_node("send_to_llm", send_to_llm)
builder.add_node("answer_to_user", send_to_user)

# Edges
builder.add_edge(START, "choose_resolver")
builder.add_conditional_edges("choose_resolver", route_query)
builder.add_edge("send_to_supprot", END)
builder.add_edge("send_to_llm", "answer_to_user")
builder.add_edge("answer_to_user", END)

graph = builder.compile()

# Visual
# with open("04_tools_agents/graph_example.png", "wb") as f:
#     f.write(graph.get_graph().draw_mermaid_png())

# Graph invoke
res = graph.invoke({"query": "Hi, I can't connect to DB in my department"})
print("---" * 33)
print(res)