# AI Research Assistant RAG System

A professional Multi-Agent Retrieval-Augmented Generation (RAG) application designed to provide intelligent document-based question answering using semantic search, vector embeddings, and contextual AI responses.

The system allows users to upload documents such as PDF, TXT, and Markdown files, build a searchable vector knowledge base, and interact with documents through a modern AI-powered chat interface.

---

# Project Overview

The AI Research Assistant RAG System combines modern AI orchestration, vector search, and conversational memory to create an intelligent document assistant capable of understanding and answering user queries from uploaded files.

This project is built using:

- FastAPI for backend APIs
- LangGraph for multi-agent orchestration
- ChromaDB for vector storage
- Sentence Transformers for embeddings
- HTML/CSS/JavaScript + Bootstrap for frontend UI

The application supports semantic retrieval, contextual conversations, and responsive AI-chat interactions.

---

# Features

- Multi-Agent RAG workflow using LangGraph
- Semantic document retrieval
- ChromaDB vector database integration
- PDF, TXT, and Markdown document upload
- Automatic document chunking & embeddings
- Context-aware AI question answering
- Conversation history & memory
- Responsive AI assistant UI
- RESTful API architecture
- Real-time frontend interaction
- Frontend deployment on Vercel
- Backend deployment on Render

---

# Technology Stack

## Backend
- Python
- FastAPI
- LangGraph
- ChromaDB
- Sentence Transformers
- Uvicorn

## Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap 5
- Bootstrap Icons

## Deployment
- Vercel (Frontend)
- Render (Backend)

---

# System Architecture

The application follows a modular Multi-Agent architecture.

### Agents Used

| Agent | Responsibility |
|------|----------------|
| Query Analysis Agent | Understands user queries |
| Retrieval Agent | Retrieves relevant vector chunks |
| Re-ranking Agent | Reorders retrieved results |
| Generation Agent | Generates final AI response |
| Citation Agent | Handles source references |

LangGraph orchestrates the workflow between all agents.

---

# Folder Structure

```bash
AI-Research-Assistant-RAG/
│
├── backend/
│   ├── agents/
│   ├── services/
│   ├── uploads/
│   ├── chroma_db/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
│
├── sample_docs/
├── .gitignore
└── README.md
