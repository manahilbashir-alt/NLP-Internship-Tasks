from pydantic import BaseModel
from typing import List, Dict


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str


class SessionInfo(BaseModel):
    session_id: str
    message_count: int


class ErrorResponse(BaseModel):
    error: str
    detail: str