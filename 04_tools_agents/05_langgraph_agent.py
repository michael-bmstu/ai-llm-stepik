import os
from dotenv import load_dotenv
from typing_extensions import TypedDict, Annotated
from collections.abc import Sequence
from pydantic import BaseModel, Field

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

load_dotenv()