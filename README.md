# 🤖 Enterprise AI Assistant

An enterprise-grade AI assistant built with **LangGraph**, **LangChain**, and **Retrieval-Augmented Generation (RAG)**. It intelligently routes user queries between conversational AI and enterprise knowledge retrieval while dynamically invoking tools when required to provide accurate, context-aware responses.

<p align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![LangChain](https://img.shields.io/badge/LangChain-Framework-green?style=for-the-badge)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic_AI-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-success?style=for-the-badge)

</p>

---

## 📖 Overview

Enterprise AI Assistant is an intelligent assistant designed to answer both general and enterprise-specific questions.

The system uses an **agentic workflow** that first determines the nature of the user's request. General conversations are handled directly by the LLM, which can invoke external tools whenever necessary. Enterprise-related questions are processed through an advanced Retrieval-Augmented Generation (RAG) pipeline, ensuring responses are grounded in uploaded documents and external knowledge when needed.

By combining intelligent routing, document retrieval, tool calling, and response evaluation, the assistant delivers reliable and context-aware answers.

---

## ✨ Features

- 🤖 Intelligent query routing
- 💬 Natural conversational AI
- 🛠️ Dynamic tool calling
- 📄 Multi-document PDF chat
- 🔍 Retrieval-Augmented Generation (RAG)
- ✅ Corrective RAG (CRAG)
- 🧠 Self-RAG response evaluation
- 🔄 Automatic query rewriting
- 🌐 Web search fallback
- 📚 Citation-supported answers
- 💾 Multi-thread conversation support
- ⚡ FastAPI backend
- 🐳 Docker support

---

## ⚙️ Workflow

```text
                    User Query
                         │
                         ▼
                  Intent Router
                  /            \
                 /              \
                ▼                ▼
        General Chat         RAG Pipeline
              │                   │
              │             Retrieve Documents
              │                   │
              │             Grade Documents
              │                   │
              │          ┌────────┴────────┐
              │          │                 │
              │          ▼                 ▼
              │    Generate         Rewrite Query
              │    Response               │
              │                           ▼
              │                     Web Search
              │                           │
              └──────────────┬────────────┘
                             ▼
                    Response Generation
                             │
                             ▼
                     Self Evaluation
                             │
                             ▼
                      Final Response
```

### Chat Workflow

The conversational branch supports dynamic tool execution.

```text
User Query
      │
      ▼
  Chat Node
      │
      ▼
     LLM
      │
 ┌────┴────┐
 │         │
 ▼         ▼
Reply   Tool Call
            │
            ▼
       Tool Execution
            │
            ▼
      Tool Response
            │
            ▼
           LLM
            │
            ▼
     Final Answer
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| Language | Python |
| AI Framework | LangChain |
| Agent Framework | LangGraph |
| LLM Provider | Groq |
| Embeddings | Hugging Face |
| Vector Database | FAISS |
| Backend | FastAPI |
| Containerization | Docker |

---

## 🚀 Getting Started

### Clone the Repository

```bash
git clone https://github.com/your-username/enterprise-ai-assistant.git

cd enterprise-ai-assistant
```

### Create a Virtual Environment

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

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 🔑 Environment Variables

Create a `.env` file in the project root and add the following variables:

```env
HF_TOKEN=your_huggingface_token

GROQ_API_KEY=your_groq_api_key

TAVILY_API_KEY=your_tavily_api_key

LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=Enterprise-AI-Assistant
```

### Run the Application

```bash
streamlit run app.py
```

---

## 💡 Use Cases

- Enterprise Knowledge Assistant
- Internal Documentation Search
- HR Policy Assistant
- Technical Documentation Q&A
- AI Research Assistant
- Company Knowledge Base

---

## 🗺️ Roadmap

- [x] Intelligent query routing
- [x] Multi-PDF support
- [x] Retrieval-Augmented Generation (RAG)
- [x] Corrective RAG (CRAG)
- [x] Self-RAG evaluation
- [x] Dynamic tool calling
- [x] Query rewriting
- [x] Citation support
- [x] Multi-thread conversations
- [ ] SQL database tool
- [ ] Long-term memory
- [ ] Multi-agent collaboration
- [ ] MCP integration
- [ ] Authentication & authorization

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Sujal Patwa**

📧 **sujalkumarpatwa1@gmail.com**

If you find this project useful, consider giving it a ⭐ on GitHub.
