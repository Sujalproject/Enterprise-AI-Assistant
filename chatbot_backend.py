from langgraph.graph import StateGraph,START,END
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from langgraph.prebuilt import ToolNode, tools_condition #tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage,HumanMessage
from langgraph.graph.message import add_messages
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
import requests




class MyInput(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
load_dotenv() 
model = ChatGroq(
        model="llama-3.3-70b-versatile",
    )


#---------------tool----------------------#
search_tool = DuckDuckGoSearchRun(region="us-en")
@tool
def calculator(first_num: float, second_num: float, operation: str) -> dict:
    """Calculate using exactly one of:
    add, sub, mul, div

    Example:
    first_num=5
    second_num=3
    operation='add'
    """
    try:
        if operation == "add":
            result = first_num + second_num
        elif operation == "sub":
            result = first_num - second_num
        elif operation == "mul":
            result = first_num * second_num
        elif operation == "div":
            if second_num == 0:
                return {"error": "Division by zero is not allowed"}
            result = first_num / second_num
        else:
            return {"error": f"Unsupported operation '{operation}'"}
        
        return {"first_num": first_num, "second_num": second_num, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def stock_price(symbol:str)->dict:
    """Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=498C4A3DJ77YSZ3G"
    response = requests.get(url)
    return response.json()

tools = [search_tool,stock_price,calculator]
llm_with_tools = model.bind_tools(tools)

def chat_node(state: MyInput):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

tool_node = ToolNode(tools)

conn = sqlite3.connect(database = 'chatbot.db', check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
graph = StateGraph(MyInput)
graph.add_node("chat_node", chat_node)
graph.add_node("tools",tool_node)
graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node",tools_condition)
graph.add_edge('tools', 'chat_node')

chatbot = graph.compile(checkpointer=checkpointer)

def all_thread_id():
    all_thread = set()
    for checkpoint in checkpointer.list(None):
        all_thread.add(checkpoint.config['configurable']['thread_id'])
    return list(all_thread)
