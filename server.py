"""
Entry point to run the FastAPI backend server.

Usage:
    python server.py
    python server.py --host 0.0.0.0 --port 8080
"""

import argparse
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api import router


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title="Enterperise AI Assistant",
        version="1.0.0",
        description="Enterprise AI Assistant with RAG and tool support.",
    )

    # Allow frontend origins to connect (adjust in production)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix="/api")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    frontend_dir = Path(__file__).resolve().parent / "frontend"
    if frontend_dir.is_dir():
        app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

    return app


app = create_app()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the chatbot API server.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    uvicorn.run(
        "server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )

