from typing import NotRequired, TypedDict, Annotated,List,Literal
from langchain_core.documents import Document
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()

class MyInput(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

    route: NotRequired[Literal["rag", "chat"]]
    question: NotRequired[str]

    doc: NotRequired[List[Document]]
    good_doc: NotRequired[List[Document]]
    web_docs: NotRequired[List[Document]]

    verdict: NotRequired[str]
    reason: NotRequired[str]

    refined_context: NotRequired[str]
    answer: NotRequired[str]

    issup: NotRequired[Literal["fully_supported", "partially_supported", "no_support"]]
    evidence: NotRequired[List[str]]

    retries: NotRequired[int]

    isuse: NotRequired[Literal["useful", "not_useful"]]
    use_reason: NotRequired[str]

    retrieval_query: NotRequired[str]
    rewrite_tries: NotRequired[int]
    

model=ChatGroq(model="qwen/qwen3.8-27b")

embeddings_model = HuggingFaceEmbeddings(
    model_name="BAAI/bge-base-en-v1.5"
)

from tools import tools
llm_with_tools=model.bind_tools(tools)
