import uuid
import streamlit as st
from graph import chatbot
from langchain_core.messages import HumanMessage

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
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if state is None:
        return []

    return state.values.get("messages", [])
