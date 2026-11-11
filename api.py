"""
FastAPI API endpoints for the LangGraph chatbot.

Provides REST endpoints for:
  - Chat (streaming & non-streaming)
  - Chat history retrieval
  - Thread listing
  - PDF upload for RAG ingestion
"""

import uuid
import traceback

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from graph import chatbot
from memory import all_thread_id
from rag.ingest import ingest_pdf


router = APIRouter()


# ── Request / Response schemas ────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User message text")
    thread_id: str | None = Field(
        default=None,
        description="Existing thread ID. A new one is generated when omitted.",
    )


class ChatResponse(BaseModel):
    thread_id: str
    reply: str


class MessageOut(BaseModel):
    role: str
    content: str


class ThreadHistoryResponse(BaseModel):
    thread_id: str
    messages: list[MessageOut]


class ThreadListResponse(BaseModel):
    thread_ids: list[str]


class UploadResponse(BaseModel):
    thread_id: str
    status: str
    documents: int
    files: int


# ── Helpers ───────────────────────────────────────────────────────────────

def _make_config(thread_id: str) -> dict:
    """Build the LangGraph config dict for a given thread."""
    return {
        "configurable": {"thread_id": thread_id},
        "metadata": {"thread_id": thread_id},
        "run_name": "chat_turn",
    }


def _serialize_message(msg) -> MessageOut:
    """Convert a LangChain message to a simple role/content dict."""
    if isinstance(msg, HumanMessage):
        role = "user"
    elif isinstance(msg, AIMessage):
        role = "assistant"
    elif isinstance(msg, ToolMessage):
        role = "tool"
    else:
        role = "unknown"
    return MessageOut(role=role, content=msg.content)


def _format_sse_data(text: str) -> str:
    """Format a text payload as valid SSE data lines (handling newlines safely)."""
    lines = text.split("\n")
    return "".join(f"data: {line}\n" for line in lines) + "\n"


def _extract_reply(result: dict) -> str:
    """Extract the assistant's reply from either the RAG answer field or chat messages."""
    if result.get("route") == "rag":
        return result.get("answer") or ""

    for msg in reversed(result.get("messages", [])):
        if isinstance(msg, AIMessage) and msg.content:
            return msg.content
    return ""


# ── Endpoints ─────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Send a message and receive the full assistant reply."""
    thread_id = request.thread_id or str(uuid.uuid4())
    config = _make_config(thread_id)

    try:
        result = chatbot.invoke(
            {"messages": [HumanMessage(content=request.message)]},
            config=config,
        )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Graph execution failed: {exc}",
        )

    ai_reply = _extract_reply(result)
    return ChatResponse(thread_id=thread_id, reply=ai_reply)


@router.post("/chat/stream")
def chat_stream(request: ChatRequest):
    """Send a message and stream assistant tokens back as server-sent events."""
    thread_id = request.thread_id or str(uuid.uuid4())
    config = _make_config(thread_id)

    def event_generator():
        rag_answer = ""
        emitted_rag = False

        try:
            for mode, chunk in chatbot.stream(
                {"messages": [HumanMessage(content=request.message)]},
                config=config,
                stream_mode=["messages", "updates"],
            ):
                if mode == "messages":
                    message_chunk, metadata = chunk
                    # Only stream tokens from the conversational 'chat' node;
                    # internal RAG nodes emit structured JSON and unverified drafts.
                    if (
                        metadata.get("langgraph_node") == "chat"
                        and isinstance(message_chunk, AIMessage)
                        and message_chunk.content
                    ):
                        yield _format_sse_data(message_chunk.content)

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
                                yield _format_sse_data(rag_answer)

            yield "data: [DONE]\n\n"
        except Exception as exc:
            traceback.print_exc()
            yield f"event: error\ndata: {exc}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Thread-Id": thread_id,
        },
    )


@router.get("/threads", response_model=ThreadListResponse)
def list_threads():
    """List all existing chat thread IDs."""
    try:
        thread_ids = all_thread_id()
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list threads: {exc}",
        )
    return ThreadListResponse(thread_ids=thread_ids)


@router.get("/threads/{thread_id}/history", response_model=ThreadHistoryResponse)
def get_thread_history(thread_id: str):
    """Retrieve the full message history for a thread."""
    try:
        state = chatbot.get_state(
            config={"configurable": {"thread_id": thread_id}}
        )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load thread state: {exc}",
        )

    raw_messages = state.values.get("messages", [])
    if not raw_messages:
        raise HTTPException(
            status_code=404,
            detail=f"Thread '{thread_id}' not found or has no messages.",
        )

    messages = [_serialize_message(m) for m in raw_messages]
    return ThreadHistoryResponse(thread_id=thread_id, messages=messages)


@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    thread_id: str | None = Form(default=None),
):
    """Upload a PDF to ingest into the RAG vector store for a thread."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted.",
        )

    thread_id = thread_id or str(uuid.uuid4())

    try:
        file_bytes = await file.read()
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read uploaded file: {exc}",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty.",
        )

    try:
        result = ingest_pdf(
            file_bytes=file_bytes,
            thread_id=thread_id,
            filename=file.filename,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except IndexError:
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in the uploaded PDF.",
        )
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"PDF ingestion failed: {exc}",
        )

    return UploadResponse(
        thread_id=thread_id,
        status=result["status"],
        documents=result["documents"],
        files=result["files"],
    )

