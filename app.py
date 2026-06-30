import streamlit as st
from utils import generate_thread_id, reset_chat, load_chat_history, add_thread
from chatbot import stream_chat
from memory import all_thread_id
from langchain_core.messages import HumanMessage

# ---- Session State ----
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_thread_ids" not in st.session_state:
    st.session_state["chat_thread_ids"] = all_thread_id()

add_thread(st.session_state["thread_id"])

st.sidebar.title("Chatbot")
if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("Chat History")
for thread_id in st.session_state["chat_thread_ids"][::-1]:
    if st.sidebar.button(thread_id):
        st.session_state["thread_id"] = thread_id
        messages = load_chat_history(thread_id)

        temp_messages =[]
        
        for msg in messages:
            if isinstance(msg,HumanMessage):
                role = "user"
            else:
                role = "assistance"
        
            temp_messages.append({'role':role,'content':msg.content})
        
        st.session_state['message_history'] = temp_messages
            

for msg in st.session_state["message_history"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Type here...")

if prompt:
    stream_chat(prompt)
