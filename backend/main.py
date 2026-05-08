import os
import uuid
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.document_processor import process_document
from services.vector_store import (
    add_chunks_to_vector_store,
    search_vector_store,
    get_document_chunks,
    clear_vector_store
)
from services.memory import (
    add_to_history,
    get_history,
    clear_history
)
from agents.graph import run_agent_graph


app = FastAPI(
    title="Advanced Document Q&A RAG System",
    description="Multi-Agent RAG System using LangGraph",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/")
def home():
    return {
        "message": "RAG Backend is running successfully",
        "status": "active"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "FastAPI RAG Backend"
    }


@app.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file selected.")

    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in [".pdf", ".txt", ".md"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, TXT, and MD files are supported."
        )

    document_id = str(uuid.uuid4())

    safe_filename = file.filename.replace("/", "_").replace("\\", "_")
    stored_filename = f"{document_id}_{safe_filename}"
    file_path = os.path.join(UPLOAD_DIR, stored_filename)

    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        chunks = process_document(file_path, safe_filename, document_id)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(e)}"
        )

    if not chunks:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in this document."
        )

    stored_chunks = add_chunks_to_vector_store(
        chunks,
        document_id=document_id,
        replace_document=True
    )

    return {
        "success": True,
        "message": "Document uploaded, processed, and stored successfully.",
        "document_id": document_id,
        "filename": safe_filename,
        "file_path": file_path,
        "total_chunks": len(chunks),
        "stored_chunks": stored_chunks
    }


@app.get("/search")
def search_documents(query: str, top_k: int = 5, document_id: Optional[str] = None):
    results = search_vector_store(
        query=query,
        top_k=top_k,
        document_id=document_id
    )

    return {
        "query": query,
        "top_k": top_k,
        "document_id": document_id,
        "results": results
    }


class AskRequest(BaseModel):
    question: str
    document_id: Optional[str] = None


@app.post("/ask")
def ask_question(request: AskRequest):
    question = request.question.strip()

    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")

    if not request.document_id:
        return {
            "question": question,
            "document_id": None,
            "answer": "Please upload a document first, then ask a question.",
            "citations": [],
            "agents_used": [
                "Query Analysis Agent",
                "Retrieval Agent",
                "Re-ranking Agent",
                "Generation Agent",
                "Citation Agent"
            ]
        }

    document_chunks = get_document_chunks(request.document_id)

    if not document_chunks:
        return {
            "question": question,
            "document_id": request.document_id,
            "answer": "I could not find this uploaded document in the knowledge base. Please upload it again.",
            "citations": [],
            "agents_used": [
                "Query Analysis Agent",
                "Retrieval Agent",
                "Re-ranking Agent",
                "Generation Agent",
                "Citation Agent"
            ]
        }

    final_state = run_agent_graph({
        "question": question,
        "document_id": request.document_id
    })

    answer = final_state.get(
        "answer",
        "This information is not available in the uploaded document."
    )

    citations = final_state.get("citations", [])

    add_to_history(
        question,
        answer,
        citations
    )

    return {
        "question": question,
        "document_id": request.document_id,
        "answer": answer,
        "citations": citations,
        "agents_used": [
            "Query Analysis Agent",
            "Retrieval Agent",
            "Re-ranking Agent",
            "Generation Agent",
            "Citation Agent"
        ]
    }


@app.get("/history")
def history():
    return {
        "history": get_history()
    }


@app.delete("/history")
def delete_history():
    clear_history()

    return {
        "message": "Conversation history cleared successfully"
    }


@app.delete("/vector-store")
def delete_vector_store(document_id: Optional[str] = None):
    clear_vector_store(document_id=document_id)

    return {
        "message": "Vector store cleared successfully",
        "document_id": document_id
    }