from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from models import (
    ChatRequest,
    ChatResponse,
    SessionInfo,
    ErrorResponse,
)

import logging
import time
from datetime import datetime


app = FastAPI(title="FastAPI Chat Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SYSTEM_PROMPT = "You are a helpful AI assistant."

MODEL_NAME = "demo-model"

chat_sessions = {}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)

logger = logging.getLogger(__name__)

@app.get("/")
def home():
    return {
        "message": "FastAPI Chat Server is running."
    }

@app.post(
    "/api/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def chat(request: ChatRequest):

    start = time.perf_counter()

    try:

        # Validate message
        if request.message.strip() == "":
            raise HTTPException(
                status_code=400,
                detail="Message cannot be empty."
            )

        # Create session if it doesn't exist
        if request.session_id not in chat_sessions:

            chat_sessions[request.session_id] = [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                }
            ]

        # Save user message
        chat_sessions[request.session_id].append(
            {
                "role": "user",
                "content": request.message
            }
        )

        #  AI response
        ai_response = f"You said: {request.message}"

        # Save AI response
        chat_sessions[request.session_id].append(
            {
                "role": "assistant",
                "content": ai_response
            }
        )

        # Calculate latency
        latency = round(
            (time.perf_counter() - start) * 1000,
            2
        )

        # Calculate simple token usage
        token_usage = (
            len(request.message.split())
            + len(ai_response.split())
        )

        # Logging
        logger.info(
            {
                "timestamp": datetime.now().isoformat(),
                "session_id": request.session_id,
                "model": MODEL_NAME,
                "token_usage": token_usage,
                "latency_ms": latency,
            }
        )

        return ChatResponse(
            session_id=request.session_id,
            response=ai_response
        )

    except HTTPException:
        raise

    except Exception as e:

        logger.exception(e)

        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(e),
            },
        )

@app.get(
    "/api/sessions",
    response_model=list[SessionInfo],
)
def list_sessions():

    sessions = []

    for session_id, history in chat_sessions.items():

        sessions.append(
            SessionInfo(
                session_id=session_id,
                message_count=len(history)
            )
        )

    return sessions

@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):

    if session_id not in chat_sessions:

        raise HTTPException(
            status_code=404,
            detail="Session not found."
        )

    return {
        "session_id": session_id,
        "history": chat_sessions[session_id]
    }