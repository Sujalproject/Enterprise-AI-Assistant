import streamlit as st
from graph import chatbot
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

def stream_chat(user_input):
    config = {"configurable": {"thread_id": st.session_state["thread_id"]},
          "metadata": {
              "thread_id": st.session_state["thread_id"]
          },
          "run_name":"chat_turn",
        }
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)
        
  
    with st.chat_message("assistant"):
        # Use a mutable holder so the generator can set/modify it
        status_holder = {"box": None}

        def ai_only_stream():
            rag_answer = ""
            emitted_rag = False

            for mode, chunk in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode=["messages", "updates"],
            ):
                if mode == "messages":
                    message_chunk, metadata = chunk
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

                    # Stream ONLY assistant tokens from the conversational 'chat' node
                    if (
                        metadata.get("langgraph_node") == "chat"
                        and isinstance(message_chunk, AIMessage)
                        and message_chunk.content
                    ):
                        yield message_chunk.content

                elif mode == "updates":
                    for node_name, node_output in chunk.items():
                        if not isinstance(node_output, dict):
                            continue
                        if node_name in ("generate", "revise_answer", "no_answer_found"):
                            rag_answer = node_output.get("answer", "")

                        if node_name == "no_answer_found" or (
                            node_name == "is_use"
                            and node_output.get("isuse") == "useful"
                        ):
                            if rag_answer and not emitted_rag:
                                emitted_rag = True
                                yield rag_answer

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