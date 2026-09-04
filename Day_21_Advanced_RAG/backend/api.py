import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import json
import shutil
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from ingestion.ingestion_pipeline import ingest_pdf_to_markdown
from chunking.recursive_chunker import chunk_markdown_text
from vectorstores.faiss_manager import add_document
from chat.conversational_chain import chat, retriever

app = FastAPI(title="RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

IMAGES_DIR = Path(__file__).resolve().parent / "data" / "images"
if IMAGES_DIR.exists():
    app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

UPLOAD_DIR = Path(__file__).resolve().parent / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
METADATA_PATH = Path(__file__).resolve().parent / "vectorstores" / "FAISS_db" / "metadata.json"

sessions = {}


class ChatRequest(BaseModel):
    session_id: str
    question: str


class ChatResponse(BaseModel):
    answer: str
    sources: str
    rewritten_question: Optional[str] = None
    images: list[str] = []

@app.post("/api/rag/chat", response_model=ChatResponse)
def rag_chat(request: ChatRequest):
    history = sessions.get(request.session_id, [])
    answer, sources, updated_history, rewritten, images = chat(request.question, history)
    sessions[request.session_id] = updated_history
    return ChatResponse(answer=answer, sources=sources, rewritten_question=rewritten, images=images)


@app.get("/api/rag/sources")
def list_sources():
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    sources = sorted(set(m["source_file"] for m in metadata if m.get("source_file")))
    return {"sources": sources, "total_chunks": len(metadata)}


@app.post("/api/rag/ingest")
async def ingest_document(file: UploadFile = File(...)):
    saved_path = UPLOAD_DIR / file.filename
    with open(saved_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    markdown_text = ingest_pdf_to_markdown(saved_path)
    start_index = len(json.loads(METADATA_PATH.read_text(encoding="utf-8"))) if METADATA_PATH.exists() else 0
    new_chunks = chunk_markdown_text(markdown_text, source_filename=file.filename, start_index=start_index)
    total_vectors = add_document(new_chunks)
    retriever.reload()

    return {
        "filename": file.filename,
        "chunks_added": len(new_chunks),
        "total_chunks_in_index": total_vectors,
    }

@app.get("/")
def root():
    return {"status": "RAG API is running"}

