from models import MyInput, llm_with_tools
from app_prompt import router_llm
from langchain_core.messages import HumanMessage

from helper import extract_question

def router_node(state):
    """Decide whether to use RAG or normal chat."""

    question = extract_question(state)

    system_prompt = """
    You are an intelligent query routing assistant.

    Decide which datasource should handle the user's question.

    Route to:
    - rag:
        - Questions about uploaded PDFs/documents.
        - Questions requiring information from the enterprise knowledge base.
        - Questions like "according to the document", "summarize the PDF",
          "what does the policy say", etc.

    - chat:
        - General conversation.
        - Coding help.
        - Math.
        - Greetings.
        - Tool usage.
        - Questions that do NOT require uploaded documents.

    Return ONLY valid JSON.

    The JSON must follow this exact structure:
    {
        "datasource": "rag"
    }

    The datasource value must be either "rag" or "chat".
    """

    result = router_llm.invoke([
        ("system", system_prompt),
        ("human", question)
    ])

    return {
        "route": result.datasource,
        "question": question,

        # Reset per-query state
        "retrieval_query": "",
        "answer": "",
        "doc": [],
        "good_doc": [],
        "web_docs": [],
        "web_query": "",
        "refined_context": "",
        "verdict": "",
        "reason": "",
        "issup": "",
        "evidence": [],
        "isuse": "",
        "use_reason": "",
        "retries": 0,
        "rewrite_tries": 0,
    }
def route_decision(state):
    return state["route"]


def chat_node(state):
    """LLM node that may answer or request a tool call."""
     
    messages = state["messages"]

    try:
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    except Exception as e:
        print(e)
        raise
