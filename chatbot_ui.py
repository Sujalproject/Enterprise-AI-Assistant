import streamlit as st
from langchain_core.messages import BaseMessage,HumanMessage,AIMessage,ToolMessage
from chatbot_backend import chatbot,all_thread_id
import uuid


#------------------utity functions------------------#

def generate_thread_id():
    thread_id = str(uuid.uuid4())
    return thread_id
   
def reset_chat():
    thread_id = generate_thread_id()
    st.session_state["thread_id"] = thread_id
    add_thread(st.session_state["thread_id"])
    st.session_state["message_history"] = []

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_thread_ids"]:
        st.session_state["chat_thread_ids"].append(thread_id)

def load_chat_history(thread_id):
    state = chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    )

    if state is None:
        return []

    return state.values.get("messages", [])



#-----------------session state------------------#
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []
    
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_thread_ids" not in st.session_state:
    st.session_state["chat_thread_ids"] = all_thread_id()

add_thread(st.session_state["thread_id"])


#------------------sidebar------------------#

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
            
#-------------------loading message------------------#


for message in st.session_state["message_history"]:
        with st.chat_message(message["role"]):
            
            st.text(message["content"])


#-------------------main chat interface------------------#
user_input = st.chat_input("Type here...")
config = {"configurable": {"thread_id": st.session_state["thread_id"]},
          "metadata": {
              "thread_id": st.session_state["thread_id"]
          },
          "run_name":"chat_turn",
        }
if user_input:
    
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)
        
  
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            ):
                # Lazily create & update the SAME status container when any tool runs
                if isinstance(message_chunk, ToolMessage):
                    tool_name = getattr(message_chunk, "name", "tool")
                    if status_holder["box"] is None:
                        status_holder["box"] = st.status(
                            f"🔧 Using `{tool_name}` …", expanded=True
                        )
                    else:
                        status_holder["box"].update(
                            label=f"🔧 Using `{tool_name}` …",
                            state="running",
                            expanded=True,
                        )

                # Stream ONLY assistant tokens
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content

        ai_message = st.write_stream(ai_only_stream())

        # Finalize only if a tool was actually used
        if status_holder["box"] is not None:
            status_holder["box"].update(
                label="✅ Tool finished", state="complete", expanded=False
            )

    # Save assistant message
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )