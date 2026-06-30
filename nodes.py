from models import llm_with_tools

def chat_node(state):
    """LLM node that may answer or request a tool call."""
     
    messages = state["messages"]

    try:
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        print(e)
        raise
