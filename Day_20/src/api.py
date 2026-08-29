from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .conversation_rag import ConversationalRAG


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Day 20 Conversational RAG API",
    description=(
        "Conversational RAG API with session memory, "
        "Chroma retrieval, contextualized follow-up "
        "questions, and source citations."
    ),
    version="1.0.0",
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    session_id: str
    message: str


# ============================================================
# RESPONSE MODEL
# ============================================================

class ChatResponse(BaseModel):

    session_id: str
    question: str
    contextualized_question: str
    answer: str
    sources: List[str]
    history_length: int


# ============================================================
# INITIALIZE RAG SYSTEM
# ============================================================

print("=" * 80)
print("INITIALIZING DAY 20 CONVERSATIONAL RAG")
print("=" * 80)

rag = ConversationalRAG()

print("=" * 80)
print("RAG SYSTEM READY")
print("=" * 80)


# ============================================================
# ROOT / HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "status": "online",
        "service": "Day 20 Conversational RAG API",
    }


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post(
    "/api/rag/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest):

    # --------------------------------------------------------
    # Validate session ID
    # --------------------------------------------------------

    if not request.session_id.strip():

        raise HTTPException(
            status_code=400,
            detail="session_id cannot be empty.",
        )

    # --------------------------------------------------------
    # Validate message
    # --------------------------------------------------------

    if not request.message.strip():

        raise HTTPException(
            status_code=400,
            detail="message cannot be empty.",
        )

    try:

        # ----------------------------------------------------
        # Run conversational RAG
        # ----------------------------------------------------

        result = rag.chat(
            session_id=request.session_id,
            question=request.message,
        )

        # ----------------------------------------------------
        # Format citations
        # ----------------------------------------------------

        formatted_sources = []

        for source in result["sources"]:

            filename = source.get(
                "filename",
                source.get(
                    "source",
                    "unknown"
                ),
            )

            page = source.get(
                "page",
                1
            )

            citation = (
                f"{filename} "
                f"(Page {page})"
            )

            if citation not in formatted_sources:

                formatted_sources.append(
                    citation
                )

        # ----------------------------------------------------
        # Return response
        # ----------------------------------------------------

        return ChatResponse(
            session_id=result[
                "session_id"
            ],

            question=result[
                "question"
            ],

            contextualized_question=result[
                "contextualized_question"
            ],

            answer=result[
                "answer"
            ],

            sources=formatted_sources,

            history_length=result[
                "history_length"
            ],
        )

    except Exception as e:

        print(
            f"ERROR in /api/rag/chat: {e}"
        )

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


# ============================================================
# GET SESSION HISTORY
# ============================================================

@app.get(
    "/api/rag/session/{session_id}"
)
def get_session(
    session_id: str
):

    history = rag.get_history(
        session_id
    )

    return {
        "session_id": session_id,
        "message_count": len(history),
        "messages": history,
    }


# ============================================================
# DELETE SESSION
# ============================================================

@app.delete(
    "/api/rag/session/{session_id}"
)
def clear_session(
    session_id: str
):

    if session_id in rag.sessions:

        del rag.sessions[
            session_id
        ]

        return {
            "status": "deleted",
            "session_id": session_id,
        }

    return {
        "status": "not_found",
        "session_id": session_id,
    }