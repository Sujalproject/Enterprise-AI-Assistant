from models import MyInput
from typing import List, Literal
from langchain_core.documents import Document
from langchain_core.runnables import RunnableConfig
from langchain_community.tools.tavily_search import TavilySearchResults
from .prompt import doc_eval_chain,filter_chain,rewrite_chain,generation_prompt,issup_llm_chain,revise_prompt,isuse_llm_chain,rewrite_llm_chain
from .retriever import _get_retriever
from helper import decompose_to_sentences, extract_question
from dotenv import load_dotenv
from models import model

load_dotenv()

def retrieve_node(state:MyInput, config:RunnableConfig):
    """RAG node that retrieves relevant documents based on the question."""
    
    question = state.get("retrieval_query") or extract_question(state)
    # Here you would implement your retrieval logic, e.g., using a vector store or search engine.
    # For demonstration, let's assume we have a function `retrieve_documents` that does this.
    thread_id = config.get("configurable", {}).get("thread_id")
    retriever = _get_retriever(thread_id)
    retrieved_docs = retriever.invoke(question) if retriever else []
    
    return {
        "question": question,
        "doc": retrieved_docs
    }

UPPER_BOUND = 0.7
LOWER_BOUND = 0.3

def eval_doc(state):
    """RAG node that evaluates the relevance of retrieved documents."""
    question = state["question"]
    scores: List[float] = []
    good: List[Document] = []
    
    
    for doc in state["doc"]:
        out= doc_eval_chain.invoke({"question": question, "chunk": doc.page_content})
        scores.append(out.score)
        
       # Keep any doc above LOWER_BOUNDas "weakly relevant"
        if out.score > LOWER_BOUND:
            good.append(doc)

    # CORRECT: at least one doc > UPPER_BOUND
    if any(s > UPPER_BOUND for s in scores):
        return {
            "good_doc": good,
            "verdict": "CORRECT",
            "reason": f"At least one retrieved chunk scored > {UPPER_BOUND}.",
        }
     # INCORRECT: all docs < LOWER_BOUND
    if len(scores) > 0 and all(s < LOWER_BOUND for s in scores):
        return {
            "good_doc": [],
            "verdict": "INCORRECT",
            "reason": f"All retrieved chunks scored < {LOWER_BOUND}.",
        }
    # AMBIGUOUS: otherwise
    return {
        "good_doc": good,
        "verdict": "AMBIGUOUS",
        "reason": f"No chunk scored > {UPPER_BOUND}, but not all were < {LOWER_BOUND}.",
    }
    
def refine(state: MyInput) -> MyInput:
    q = state["question"]

    if state.get("verdict") == "CORRECT":
        docs_to_use = state["good_doc"]
    elif state.get("verdict") == "INCORRECT":
        docs_to_use = state["web_docs"]
    else:  # AMBIGUOUS
        docs_to_use = state["good_doc"] + state["web_docs"]

    context = "\n\n".join(d.page_content for d in docs_to_use).strip()

    strips = decompose_to_sentences(context)

    kept: List[str] = []
    for s in strips:
        if filter_chain.invoke({"question": q, "sentence": s}).keep:
            kept.append(s)

    refined_context = "\n".join(kept).strip()

    return {
        "refined_context": refined_context,
    }
    

def rewrite_query(state):
    out = rewrite_chain.invoke({"question": state["question"]})
    return {"web_query": out.query}

tavily = TavilySearchResults(max_results=5)

def web_search_node(state: MyInput) -> MyInput:
    q = state.get("web_query") or state["question"]
    results = tavily.invoke({"query": q})

    web_docs: List[Document] = []
    for r in results or []:
        title = r.get("title", "")
        url = r.get("url", "")
        content = r.get("content", "") or r.get("snippet", "")
        text = f"TITLE: {title}\nURL: {url}\nCONTENT:\n{content}"
        web_docs.append(Document(page_content=text, metadata={"url": url, "title": title}))

    return {"web_docs": web_docs}

def route_after_eval(state: MyInput) -> str:
    if state["verdict"] == "CORRECT":
        return "refine"
    else:
        return "rewrite_query"
    
def generate_from_context(state: MyInput) -> MyInput:
    context = state.get("refined_context")
    if not context:
        return {"answer": "",}
    out = model.invoke(
        generation_prompt.format_messages(question=state["question"], context=context)
    )
    return {"answer": out.content}

def is_sup(state: MyInput) -> MyInput:
    decision = issup_llm_chain.invoke({
            'question': state["question"],
            'answer': state.get("answer", ""),
            'context': state.get("refined_context", ""),
        })
    return {"issup": decision.issup, "evidence": decision.evidence}

MAX_RETRIES = 10

def route_after_issup(state: MyInput) -> Literal["accept_answer", "revise_answer"]:
    # fully supported -> move forward to IsUSE (via "accept_answer" label)
    if state.get("issup") == "fully_supported":
        return "accept_answer"

    if state.get("retries", 0) >= MAX_RETRIES:
        return "accept_answer"  # will go to is_use, then likely not_useful -> no_answer_found

    return "revise_answer"

def accept_answer(state: MyInput):
    return {}

def revise_answer(state: MyInput):
    out = model.invoke(
        revise_prompt.format_messages(
            question=state["question"],
            answer=state.get("answer", ""),
            context=state.get("refined_context", ""),
        )
    )
    return {
        "answer": out.content,
        "retries": state.get("retries", 0) + 1, 
    }
    
def is_use(state: MyInput) -> MyInput:
    decision= isuse_llm_chain.invoke(
        {
            "question": state["question"],
            "answer": state.get("answer", ""),
        }
    )
    return {"isuse": decision.isuse, "use_reason": decision.reason}

MAX_REWRITE_TRIES = 3  # tune (2–4 is usually fine)

def route_after_isuse(state: MyInput) -> Literal["END", "rewrite_question", "no_answer_found"]:
    if state.get("isuse") == "useful":
        return "END"

    if state.get("rewrite_tries", 0) >= MAX_REWRITE_TRIES:
        return "no_answer_found"

    return "rewrite_question"

def rewrite_question(state: MyInput):
    decision= rewrite_llm_chain.invoke({
            "question": state["question"],
            "retrieval_query": state.get("retrieval_query", ""),
            "answer": state.get("answer", ""),
        }
    )

    return {
        "retrieval_query": decision.retrieval_query,
        "rewrite_tries": state.get("rewrite_tries", 0) + 1,
    }
    
def no_answer_found(state: MyInput):
    return {"answer": "No answer found.", "context": ""}