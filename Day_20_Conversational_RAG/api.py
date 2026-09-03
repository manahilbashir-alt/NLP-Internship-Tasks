from fastapi import FastAPI
from pydantic import BaseModel

from conversational_chain import chat


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Conversational RAG API",
    description="Day 20 Conversational RAG API",
    version="1.0"
)


# ============================================================
# SESSION MEMORY
# ============================================================

session_histories = {}


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    session_id: str
    question: str


# ============================================================
# RESPONSE MODEL
# ============================================================

class ChatResponse(BaseModel):

    session_id: str
    question: str
    rewritten_question: str
    answer: str
    sources: str


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Conversational RAG API is running"
    }


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post(
    "/api/rag/chat",
    response_model=ChatResponse
)
def rag_chat(request: ChatRequest):

    session_id = request.session_id

    question = request.question

    # Get existing history for this session
    history = session_histories.get(
        session_id,
        []
    )

    # Run conversational RAG
    result = chat(
        question,
        history
    )

    # Save updated history
    session_histories[session_id] = result[
        "history"
    ]

    return ChatResponse(

        session_id=session_id,

        question=question,

        rewritten_question=result[
            "rewritten_question"
        ],

        answer=result[
            "answer"
        ],

        sources=result[
            "sources"
        ]
    )


# ============================================================
# CLEAR SESSION
# ============================================================

@app.delete("/api/rag/chat/{session_id}")
def clear_session(session_id: str):

    if session_id in session_histories:

        del session_histories[session_id]

        return {
            "message": "Session history cleared",
            "session_id": session_id
        }

    return {
        "message": "Session not found",
        "session_id": session_id
    }