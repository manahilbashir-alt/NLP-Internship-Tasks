"""
Run once at DOCKER BUILD TIME to download and cache all model weights
into the image layer. This is what prevents a multi-GB download from
happening on the first real user request in production.

Add/remove blocks here to match whatever your app.py actually loads.
"""

import os

WHISPER_MODEL_NAME = os.environ.get("WHISPER_MODEL_NAME", "small")
XTTS_MODEL_NAME = os.environ.get(
    "XTTS_MODEL_NAME", "tts_models/multilingual/multi-dataset/xtts_v2"
)
EMBEDDING_MODEL_NAME = os.environ.get(
    "EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"
)

print(f"[warm_models] Caching Whisper model: {WHISPER_MODEL_NAME}")
# faster-whisper (recommended for CPU hosts — ~4x faster than openai-whisper)
from faster_whisper import WhisperModel  # noqa: E402

WhisperModel(WHISPER_MODEL_NAME, device="cpu", compute_type="int8")

print(f"[warm_models] Caching XTTS v2 model: {XTTS_MODEL_NAME}")
from TTS.api import TTS  # noqa: E402

TTS(XTTS_MODEL_NAME, progress_bar=False)

print(f"[warm_models] Caching embedding model: {EMBEDDING_MODEL_NAME}")
from sentence_transformers import SentenceTransformer  # noqa: E402

SentenceTransformer(EMBEDDING_MODEL_NAME)

print("[warm_models] All model weights cached successfully.")
