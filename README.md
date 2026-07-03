# 🤖 Enterprise AI Assistant

An enterprise-grade AI assistant powered by **Large Language Models (LLMs)**, **LangGraph**, and **LangChain**. The assistant intelligently routes user queries between conversational AI and an advanced Retrieval-Augmented Generation (RAG) pipeline while supporting dynamic tool execution, web search, and end-to-end observability through **LangSmith**.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-Framework-green?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic%20AI-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

</p>

---

# 📖 Overview

Enterprise AI Assistant is an intelligent assistant designed to answer both general-purpose and enterprise-specific questions.

The assistant first analyzes the user's query and intelligently routes it to the most suitable workflow. General conversations are handled through an LLM capable of invoking external tools whenever required. Enterprise-specific questions are processed through a Retrieval-Augmented Generation (RAG) pipeline, enabling grounded responses based on uploaded documents and external knowledge sources.

To improve answer quality, the system incorporates **Corrective RAG (CRAG)**, **Self-RAG**, automatic query rewriting, and web search fallback. Additionally, **LangSmith** is integrated to provide complete observability of the agent workflow, making debugging, monitoring, and performance analysis easier.

---

# ✨ Features

- 🤖 Intelligent query routing
- 💬 General conversational AI
- 🛠️ Dynamic tool calling
- 📄 Multi-PDF document question answering
- 🔍 Retrieval-Augmented Generation (RAG)
- ✅ Corrective RAG (CRAG)
- 🧠 Self-RAG response evaluation
- 🔄 Automatic query rewriting
- 🌐 Web search integration using Tavily
- 📚 Citation-supported responses
- 💾 Multi-thread conversations
- 📊 End-to-end observability using LangSmith
- ⚡ FastAPI backend
- 🐳 Dockerized deployment

---

# 🏗️ Architecture

```text
                          User Query
                               │
                               ▼
                        Intelligent Router
                      ┌─────────┴─────────┐
                      │                   │
                      ▼                   ▼
               General Chat          RAG Pipeline
                      │                   │
               LLM with Tools      Retrieve Documents
                      │                   │
          ┌───────────┴───────────┐       ▼
          │                       │   Grade Documents
          ▼                       │       │
   Direct Response                │       ▼
                                  │  Relevant?
                                  │   │      │
                                  │ Yes      No
                                  │   │      │
                                  │   ▼      ▼
                                  │Generate Rewrite Query
                                  │Answer       │
                                  │             ▼
                                  │       Web Search
                                  │             │
                                  └──────┬──────┘
                                         ▼
                                Self-RAG Evaluation
                                         │
                                         ▼
                                  Final Response
```

---

# 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| AI Framework | LangChain |
| Agent Framework | LangGraph |
| LLM Provider | Groq |
| Embeddings | Hugging Face |
| Vector Store | FAISS |
| Web Search | Tavily |
| Observability | LangSmith |
| Backend | FastAPI |
| Containerization | Docker |

---

# 📊 Observability

This project integrates **LangSmith** to provide comprehensive observability across the entire agent workflow.

### LangSmith enables:

- Visualizing LangGraph execution flow
- Tracking every node execution
- Monitoring LLM requests and responses
- Inspecting tool invocations
- Debugging retrieval pipelines
- Measuring latency and execution time
- Simplifying troubleshooting and performance optimization

---

# 🚀 Getting Started

## Clone the Repository

```bash
git clone https://github.com/your-username/enterprise-ai-assistant.git

cd enterprise-ai-assistant
```

## Create a Virtual Environment

```bash
python -m venv .venv
```

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure Environment Variables

Create a `.env` file in the project root.

```env
HF_TOKEN=your_huggingface_token

GROQ_API_KEY=your_groq_api_key

TAVILY_API_KEY=your_tavily_api_key

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=Enterprise-AI-Assistant
```

---

## Run the Application

```bash
streamlit run app.py
```

---

# 💡 Use Cases

- Enterprise Knowledge Assistant
- HR Policy Assistant
- Internal Documentation Search
- Technical Documentation Q&A
- AI Research Assistant
- Company Knowledge Base
- Multi-document Question Answering

---

# 🛣️ Roadmap

- ✅ Intelligent Query Routing
- ✅ Agentic Workflow
- ✅ Multi-PDF Chat
- ✅ Retrieval-Augmented Generation (RAG)
- ✅ Corrective RAG (CRAG)
- ✅ Self-RAG
- ✅ Dynamic Tool Calling
- ✅ Query Rewriting
- ✅ Tavily Web Search
- ✅ LangSmith Observability
- ✅ Docker Support
- 🔄 SQL Database Tool
- 🔄 Long-Term Memory
- 🔄 MCP Integration
- 🔄 Authentication & Authorization

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a new feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

**Sujal Patwa**

📧 **sujalkumarpatwa1@gmail.com**

If you find this project helpful, consider giving it a ⭐ to support the project!
