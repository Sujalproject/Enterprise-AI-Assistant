from langgraph.graph import StateGraph, START
from langgraph.prebuilt import tools_condition
from nodes import chat_node
from tools import tool_node
from memory import checkpointer
from models import MyInput

builder=StateGraph(MyInput)
builder.add_node("chat_node",chat_node)
builder.add_node("tools",tool_node)
builder.add_edge(START,"chat_node")
builder.add_conditional_edges("chat_node",tools_condition)
builder.add_edge("tools","chat_node")

chatbot=builder.compile(checkpointer=checkpointer)
