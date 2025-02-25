# LLM Chat Dialogue with RAG and GraphRAG

This project implements a chat dialogue system that leverages Large Language Models (LLM) with Retrieval-Augmented Generation (RAG) and Graph-based RAG capabilities.

## Project Structure

```
llm-chat-dialogue/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI application entry
│   ├── rag/            # RAG implementation
│   │   └── __init__.py
│   └── models/         # Data models
│       └── __init__.py
├── frontend/
│   └── streamlit_app.py # Streamlit frontend application
├── requirements.txt    # Project dependencies
└── README.md          # Project documentation
```

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the backend server:
```bash
uvicorn app.main:app --reload
```

2. Start the Streamlit frontend:
```bash
streamlit run frontend/streamlit_app.py
```
