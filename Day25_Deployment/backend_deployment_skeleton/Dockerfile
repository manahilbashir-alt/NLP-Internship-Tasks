# =========================================================
# Backend Dockerfile — FastAPI + RAG + Whisper STT + XTTS v2 TTS
# =========================================================
# Build context is this backend/ folder, e.g.:
#   cd backend && docker build -t rag-backend .
#
# CPU-only base. For GPU hosts (e.g. HF Spaces GPU tier), swap the
# base image for `nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04`
# and install a matching CUDA build of torch (see comment below).

FROM python:3.11-slim AS base

# ---- System deps -------------------------------------------------
# ffmpeg: required by Whisper/faster-whisper and TTS for audio decode
# libsndfile1: required by soundfile (used by TTS/XTTS)
# git: some TTS/HF model repos are pulled via git during first load
# build-essential: needed to compile a couple of audio deps on slim images
# curl: used by the HEALTHCHECK below
RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libsndfile1 \
        git \
        build-essential \
        curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---- Python deps ---------------------------------------------------
# Pin torch to CPU wheels explicitly to keep the image smaller and avoid
# accidentally pulling CUDA wheels on a CPU-only host.
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -r requirements.txt

# If deploying to a GPU host instead, replace the torch install line above with:
#   pip install --no-cache-dir torch==2.3.1 --index-url https://download.pytorch.org/whl/cu121
# and use the CUDA base image mentioned at the top of this file.

# ---- Cache model weights at BUILD time, not first request ---------
# This is the key step that avoids cold-start timeouts: models are
# downloaded once during `docker build` and baked into the image layer,
# so the container starts ready to serve instead of fetching ~GBs of
# weights on the first real user request.
ENV HF_HOME=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    COQUI_TOS_AGREED=1 \
    WHISPER_MODEL_NAME=small \
    XTTS_MODEL_NAME=tts_models/multilingual/multi-dataset/xtts_v2 \
    EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

RUN mkdir -p /app/.cache/huggingface

COPY scripts/warm_models.py ./scripts/warm_models.py
RUN python scripts/warm_models.py

# ---- App code -------------------------------------------------------
# .dockerignore keeps .env, __pycache__, venvs, etc. out of the image.
COPY . .

# ---- Runtime ---------------------------------------------------------
EXPOSE 8000

# Healthcheck hits the /health route defined in app/main.py, so the host
# (and docker-compose) can tell the container is actually serving, not
# just "started". If you change the app's import path, update both the
# CMD below and this URL together.
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# workers=1 because Whisper/XTTS model instances are loaded in-process and
# are memory-heavy; scale via multiple containers/replicas instead of
# multiple uvicorn workers unless you've explicitly designed for shared
# model loading (e.g. via a model server).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
