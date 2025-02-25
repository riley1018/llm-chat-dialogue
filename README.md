# LLM Chat Dialogue with RAG and GraphRAG

This project implements a chat dialogue system that leverages Large Language Models (LLM) with Retrieval-Augmented Generation (RAG) and Graph-based RAG capabilities.

## Project Structure

```
llm-chat-dialogue/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI backend entry
│   ├── rag/            # RAG implementation
│   │   └── __init__.py
│   └── models/         # Data models
│       └── __init__.py
├── static/
│   └── index.html      # HTML/JS frontend interface
├── requirements.txt    # Python dependencies
└── README.md          # Project documentation
```

## Setup Instructions

1. Clone repository:
```bash
git clone https://github.com/riley1018/llm-chat-dialogue.git
cd llm-chat-dialogue
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Start backend server:
```bash
uvicorn app.main:app --reload
```

Access the chat interface at:  
http://localhost:8000

## Key Features
- Modern chat interface with HTML/CSS
- Document upload capability (PDF/TXT)
- API endpoint for RAG integration
- Git version control integration
