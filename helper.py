import re
from typing import List

from langchain_core.messages import HumanMessage
from models import MyInput


def extract_question(state: MyInput) -> str:
    """Return the latest user question."""
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return message.content

    raise ValueError("No HumanMessage found in state.")


def decompose_to_sentences(text: str) -> List[str]:
    text = re.sub(r"\s+", " ", text).strip()
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 20]