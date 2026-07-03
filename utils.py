import uuid
import streamlit as st
from graph import chatbot

from typing import List
from langchain_core.messages import HumanMessage

from models import MyInput

def generate_thread_id():
    return str(uuid.uuid4())

def add_thread(tid):
    if tid not in st.session_state["chat_thread_ids"]:
        st.session_state["chat_thread_ids"].append(tid)

def reset_chat():
    st.session_state["thread_id"]=generate_thread_id()
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"]=[]

def load_chat_history(thread_id):
    state = chatbot.get_state(config={"configurable": {"thread_id": thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get("messages", [])

