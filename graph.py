from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import tools_condition
from nodes import chat_node, route_decision,router_node
from tools import tool_node
from memory import checkpointer
from models import MyInput
from rag.node import refine, retrieve_node, eval_doc ,rewrite_query ,web_search_node ,route_after_eval,generate_from_context,is_sup,route_after_issup,accept_answer,revise_answer,is_use,route_after_isuse,rewrite_question,no_answer_found


builder=StateGraph(MyInput)
builder.add_node("router", router_node)
builder.add_node("chat", chat_node)
builder.add_node("tools", tool_node)

#crag
builder.add_node("retrieve", retrieve_node)
builder.add_node("eval_doc", eval_doc)
builder.add_node("rewrite_query", rewrite_query)
builder.add_node("web_search", web_search_node)
builder.add_node("refine", refine)
builder.add_node("generate", generate_from_context)

#self rag 
builder.add_node("is_sup", is_sup)
builder.add_node("is_use", is_use)
builder.add_node("revise_answer", revise_answer)
builder.add_node("rewrite_question", rewrite_question)
builder.add_node("accept_answer", accept_answer)
builder.add_node("no_answer_found", no_answer_found)


builder.add_edge(START, "router")
builder.add_conditional_edges(
    "router",
    route_decision,
    {
        "chat": "chat",
        "rag": "retrieve",
    },
)
builder.add_conditional_edges("chat",tools_condition)
builder.add_edge("tools","chat")


builder.add_edge("retrieve", "eval_doc")

builder.add_conditional_edges(
    "eval_doc",
    route_after_eval,
    {
        "refine": "refine",
        "rewrite_query": "rewrite_query",
    },
)
builder.add_edge("rewrite_query", "web_search")
builder.add_edge("web_search", "refine")
builder.add_edge("refine", "generate")

builder.add_edge("generate", "is_sup")
builder.add_conditional_edges(
    "is_sup",
    route_after_issup,
    {
        "accept_answer": "is_use",     
        "revise_answer": "revise_answer",
    },
)
builder.add_edge("revise_answer", "is_sup")
builder.add_conditional_edges(
    "is_use",
    route_after_isuse,
    {
        "END": END,
        "rewrite_question": "rewrite_question",
        "no_answer_found": "no_answer_found",
    },
)
builder.add_edge("rewrite_question", "retrieve")
chatbot=builder.compile(checkpointer=checkpointer)
