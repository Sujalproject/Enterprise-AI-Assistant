from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from typing import Annotated, Any, Dict, Optional
from models import embeddings_model
import tempfile
from .retriever import _THREAD_VECTORSTORE, _THREAD_METADATA
import os

def ingest_pdf(file_bytes: bytes, thread_id: str, filename: Optional[str] = None) -> dict:
    """
    Build a FAISS retriever for the uploaded PDF and store it for the thread.

    Returns a summary dict that can be surfaced in the UI.
    """
    if not file_bytes:
        raise ValueError("No bytes received for ingestion.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(file_bytes)
        temp_path = temp_file.name
        
    try:   
        loader = PyPDFLoader(temp_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        if thread_id not in _THREAD_VECTORSTORE:
            vectorstore = FAISS.from_documents(docs, embeddings_model)
            _THREAD_VECTORSTORE[thread_id] = vectorstore
        else:
            vectorstore = _THREAD_VECTORSTORE[thread_id]
            vectorstore.add_documents(docs)
            
        _THREAD_METADATA.setdefault(thread_id, {"files": []})

        if filename:
            _THREAD_METADATA[thread_id]["files"].append(filename)

        return {
            "status": "success",
            "documents": len(docs),
            "files": len(_THREAD_METADATA[thread_id]["files"]),
        }

    finally:
        os.remove(temp_path)
        
        
