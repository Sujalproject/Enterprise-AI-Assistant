from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

class MyInput(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

model=ChatGroq(model="llama-3.3-70b-versatile")

from tools import tools
llm_with_tools=model.bind_tools(tools)
