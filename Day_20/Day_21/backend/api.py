
from pathlib import Path
import shutil

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion import (
    extract_text,
    chunk_text
)

from rag import (
    add_documents,
    get_sources
)

from chat import (
    chat_with_rag,
    get_session_history
)


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Day 21 RAG API",
    description=(
        "Complete FastAPI backend for "
        "the Day 21 RAG application"
    ),
    version="1.0.0"
)


# ============================================================
# CORS CONFIGURATION
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DIRECTORIES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "data" / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    session_id: str

    question: str

    top_k: int = 3


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Day 21 RAG API is running"
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# DOCUMENT INGESTION
# ============================================================

@app.post("/api/rag/ingest")
async def ingest_document(
    file: UploadFile = File(...)
):
    """
    Upload and process PDF, DOCX or TXT documents.
    """

    allowed_extensions = {
        ".pdf",
        ".docx",
        ".txt"
    }

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="Filename is missing."
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                "Only PDF, DOCX, and TXT "
                "files are supported."
            )
        )

    # --------------------------------------------------------
    # File path
    # --------------------------------------------------------

    file_path = (
        UPLOAD_DIR / file.filename
    )

    try:

        # ----------------------------------------------------
        # Save uploaded file
        # ----------------------------------------------------

        with open(
            file_path,
            "wb"
        ) as buffer:

            shutil.copyfileobj(
                file.file,
                buffer
            )

        # ----------------------------------------------------
        # Extract text
        # ----------------------------------------------------

        text = extract_text(
            str(file_path)
        )

        if not text.strip():

            raise HTTPException(
                status_code=400,
                detail=(
                    "No text could be extracted "
                    "from the document."
                )
            )

        # ----------------------------------------------------
        # Chunk document
        # ----------------------------------------------------

        chunks = chunk_text(
            text
        )

        if not chunks:

            raise HTTPException(
                status_code=400,
                detail="Document produced no chunks."
            )

        # ----------------------------------------------------
        # Create embeddings and store in ChromaDB
        # ----------------------------------------------------

        chunk_count = add_documents(
            chunks,
            file.filename
        )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return {
            "message": (
                "Document ingested successfully"
            ),
            "filename": file.filename,
            "characters": len(text),
            "chunks": chunk_count
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# CONVERSATIONAL RAG CHAT
# ============================================================

@app.post("/api/rag/chat")
def chat(
    request: ChatRequest
):
    """
    Conversational RAG question answering.
    """

    question = request.question.strip()

    session_id = request.session_id.strip()

    # --------------------------------------------------------
    # Validate question
    # --------------------------------------------------------

    if not question:

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # --------------------------------------------------------
    # Validate session ID
    # --------------------------------------------------------

    if not session_id:

        raise HTTPException(
            status_code=400,
            detail="Session ID cannot be empty."
        )

    # --------------------------------------------------------
    # Validate top_k
    # --------------------------------------------------------

    if request.top_k < 1:

        raise HTTPException(
            status_code=400,
            detail="top_k must be at least 1."
        )

    if request.top_k > 10:

        raise HTTPException(
            status_code=400,
            detail="top_k cannot be greater than 10."
        )

    # --------------------------------------------------------
    # Generate RAG response
    # --------------------------------------------------------

    try:

        result = chat_with_rag(
            session_id=session_id,
            question=question,
            top_k=request.top_k
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# SOURCES
# ============================================================

@app.get("/api/rag/sources")
def sources():
    """
    Return all ingested documents.
    """

    try:

        return {
            "sources": get_sources()
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# SESSION HISTORY
# ============================================================

@app.get("/api/rag/chat/{session_id}/history")
def chat_history(
    session_id: str
):
    """
    Return conversation history for a session.
    """

    history = get_session_history(
        session_id
    )

    return {
        "session_id": session_id,
        "history": history
    }