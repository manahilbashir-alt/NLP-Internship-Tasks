"""
app/main.py — FastAPI entrypoint skeleton.

This wires together the three pieces the Dockerfile and deployment guide
assume exist: a /health route (for Docker's HEALTHCHECK and host uptime
checks), CORS restricted to the deployed frontend origin, and placeholder
endpoints for STT / RAG / TTS. Replace the placeholder bodies with your
actual Day 23 logic — the model loading pattern (load once at module import,
not per-request) is what matters here.
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

load_dotenv()

# ---------------------------------------------------------------------
# Load models ONCE at process startup (they were already cached into the
# image at build time by scripts/warm_models.py — this just loads them
# into memory for this running process).
# ---------------------------------------------------------------------
_whisper_model = None
_tts_model = None
_embedding_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _whisper_model, _tts_model, _embedding_model

    from faster_whisper import WhisperModel
    from TTS.api import TTS
    from sentence_transformers import SentenceTransformer

    _whisper_model = WhisperModel(
        os.environ.get("WHISPER_MODEL_NAME", "small"),
        device="cpu",
        compute_type="int8",
    )
    _tts_model = TTS(
        os.environ.get("XTTS_MODEL_NAME", "tts_models/multilingual/multi-dataset/xtts_v2"),
        progress_bar=False,
    )
    _embedding_model = SentenceTransformer(
        os.environ.get("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    )

    yield  # app runs here

    # (optional) cleanup on shutdown goes here


app = FastAPI(title="RAG + Whisper + XTTS Backend", lifespan=lifespan)

# ---------------------------------------------------------------------
# CORS — locked to the exact deployed frontend origin(s), no wildcard.
# ---------------------------------------------------------------------
allowed_origins = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Used by the Dockerfile HEALTHCHECK and by uptime monitors on the host."""
    return {
        "status": "ok",
        "whisper_loaded": _whisper_model is not None,
        "tts_loaded": _tts_model is not None,
        "embedding_loaded": _embedding_model is not None,
    }


@app.post("/api/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """Whisper STT — replace with your Day 23 implementation."""
    contents = await audio.read()
    # segments, info = _whisper_model.transcribe(io.BytesIO(contents))
    # return {"text": " ".join(s.text for s in segments)}
    raise NotImplementedError("Wire up your Day 23 Whisper transcription logic here.")


@app.post("/api/ask")
async def ask(query: str):
    """RAG retrieval + LLM generation — replace with your Day 23 implementation."""
    # 1. embed query with _embedding_model
    # 2. retrieve top-k chunks from your vector store (e.g. chromadb at VECTOR_DB_PATH)
    # 3. call your LLM with retrieved context + query
    raise NotImplementedError("Wire up your Day 23 RAG pipeline here.")


@app.post("/api/speak")
async def speak(text: str):
    """
    XTTS v2 streamed synthesis — replace with your Day 23 implementation.
    Use StreamingResponse (or a WebSocket route) so audio starts playing
    before the full clip finishes generating. Confirm which one your
    frontend actually expects before wiring this up for real.
    """

    def audio_chunk_generator():
        # for chunk in _tts_model.tts_stream(text=text, speaker_wav=os.environ["XTTS_SPEAKER_WAV_PATH"], language="en"):
        #     yield chunk
        raise NotImplementedError("Wire up your Day 23 XTTS streaming logic here.")

    return StreamingResponse(audio_chunk_generator(), media_type="audio/wav")
