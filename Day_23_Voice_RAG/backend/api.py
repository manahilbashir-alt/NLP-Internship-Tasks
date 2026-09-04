
"""
DAY 23 - MAIN API

Endpoints:

    GET  /
    GET  /api/rag/sources
    POST /api/rag/ingest
    POST /api/rag/chat
    POST /api/rag/chat/stream
    POST /api/rag/chat/voice
    POST /api/transcribe
"""

import os
import re
import json
import base64
import tempfile
import time
from pathlib import Path
from importlib.util import module_from_spec, spec_from_file_location

import requests
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import logging


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    filename="rag_api.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# ============================================================
# PATHS
# ============================================================

BACKEND_ROOT = Path(__file__).resolve().parent

RETRIEVAL_DIR = BACKEND_ROOT / "05_retrieval"
VOICE_DIR = BACKEND_ROOT / "06_voice"
IMAGES_DIR = BACKEND_ROOT / "data" / "images"

TTS_SERVICE_URL = "http://127.0.0.1:8004/api/tts/speak-one"


# ============================================================
# LOAD NUMBERED MODULES
# ============================================================

def load_module(file_path: Path, module_name: str):

    if not file_path.exists():
        raise FileNotFoundError(
            f"Module not found: {file_path}"
        )

    spec = spec_from_file_location(
        module_name,
        file_path
    )

    if spec is None or spec.loader is None:
        raise ImportError(
            f"Could not load module: {file_path}"
        )

    module = module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


# ============================================================
# STARTUP
# ============================================================

print()
print("=" * 75)
print("STARTING DAY 23 API")
print("=" * 75)


# ============================================================
# LOAD RETRIEVAL PIPELINE
# ============================================================

print()
print("[api] Loading retrieval pipeline...")

retrieval_module = load_module(
    RETRIEVAL_DIR / "07_langchain_retrieval.py",
    "day23_retrieval"
)


# ============================================================
# LOAD GEMINI
# ============================================================

print()
print("[api] Loading Gemini generation...")

gemini_module = load_module(
    RETRIEVAL_DIR / "08_gemini_generation.py",
    "day23_gemini"
)


# ============================================================
# LOAD SPEECH TO TEXT
# ============================================================

print()
print("[api] Loading speech-to-text...")

stt_module = load_module(
    VOICE_DIR / "01_speech_to_text.py",
    "day23_stt"
)


# ============================================================
# LOAD CONTENT SAFETY FILTER
# ============================================================

print()
print("[api] Loading content safety filter...")

content_filter_module = load_module(
    VOICE_DIR / "03_content_filter.py",
    "day23_content_filter"
)

moderate_text = content_filter_module.moderate_text


# ============================================================
# INITIALIZE RAG PIPELINE
# ============================================================

print()
print("[api] Initializing RAG pipeline...")

rag_pipeline = retrieval_module.LangChainRetrievalPipeline()

print()
print("[api] RAG pipeline ready.")


# ============================================================
# TRANSCRIPTION SERVICE
# ============================================================

transcription_service = stt_module.transcription_service


print()
print("[api] All components loaded. API is ready.")


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Day 23 Voice RAG API"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# STATIC IMAGES
# ============================================================

if IMAGES_DIR.exists():

    app.mount(
        "/images",
        StaticFiles(directory=IMAGES_DIR),
        name="images"
    )


# ============================================================
# SESSION MEMORY
# ============================================================

sessions: dict[str, list] = {}


# ============================================================
# REQUEST MODELS
# ============================================================

class ChatRequest(BaseModel):

    session_id: str
    question: str
    voice: bool = True


# ============================================================
# SOURCE FORMATTER
# ============================================================

def format_sources_string(documents):

    seen = set()
    lines = []

    for doc in documents:

        source_file = doc.metadata.get(
            "source",
            "MACHINE LEARNING.pdf"
        )

        page = doc.metadata.get(
            "page",
            "unknown"
        )

        key = (
            source_file,
            page
        )

        if key not in seen:

            seen.add(key)

            lines.append(
                f"- {source_file}, page {page}"
            )

    return "\n".join(lines)


# ============================================================
# IMAGE EXTRACTION
# ============================================================

def extract_image_paths(
    reranked_results,
    max_images=3
):

    image_paths = []
    seen = set()

    for result in reranked_results:

        element_type = result.get(
            "element_type"
        )

        content = result.get(
            "content",
            ""
        ).strip()

        if (
            element_type == "image"
            and content
        ):

            if content not in seen:

                seen.add(content)
                image_paths.append(content)

    return image_paths[:max_images]


# ============================================================
# SENTENCE EXTRACTION
# ============================================================

def extract_complete_sentences(buffer: str):

    matches = list(
        re.finditer(
            r'[^.!?]*[.!?]+(?:\s+|$)',
            buffer
        )
    )

    if not matches:

        return [], buffer

    last_end = matches[-1].end()

    sentences = [
        m.group().strip()
        for m in matches
        if m.group().strip()
    ]

    remainder = buffer[last_end:]

    return sentences, remainder


# ============================================================
# BLOCKED RESPONSE
# ============================================================

def blocked_response(reason: str):

    return {
        "answer": reason,
        "sources": "",
        "rewritten_question": None,
        "images": [],
        "moderated": True,
    }


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "Day 23 Voice RAG API is running"
    }


# ============================================================
# SOURCES
# ============================================================

@app.get("/api/rag/sources")
def list_sources():

    total_children = len(
        rag_pipeline.hierarchical_data.get(
            "searchable_children",
            []
        )
    )

    document_name = rag_pipeline.hierarchical_data.get(
        "document",
        "MACHINE LEARNING.pdf"
    )

    documents = rag_pipeline.hierarchical_data.get(
        "documents",
        []
    )

    if not documents:
        documents = [document_name]

    return {
        "sources": documents,
        "total_chunks": total_children,
    }


# ============================================================
# INGEST PDF
# ============================================================

@app.post("/api/rag/ingest")
async def ingest_document(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )

    if not file.filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    temp_path = None

    try:

        # ----------------------------------------------------
        # READ UPLOADED FILE
        # ----------------------------------------------------

        file_bytes = await file.read()

        if not file_bytes:

            raise HTTPException(
                status_code=400,
                detail="Uploaded PDF is empty."
            )

        # ----------------------------------------------------
        # SAVE TEMPORARY PDF
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as temp_file:

            temp_path = temp_file.name

            temp_file.write(
                file_bytes
            )

        print()
        print("=" * 75)
        print(
            f"[api] RECEIVED PDF: {file.filename}"
        )
        print("=" * 75)

        logging.info(
            f"Document upload received: {file.filename}"
        )

        # ----------------------------------------------------
        # RUN ACTUAL RAG INGESTION
        # ----------------------------------------------------

        result = rag_pipeline.ingest_document(
            pdf_path=Path(temp_path),
            document_name=file.filename
        )

        print()
        print(
            f"[api] Ingestion successful: "
            f"{result['chunks_added']} chunks added"
        )

        logging.info(
            f"Document ingestion successful: "
            f"{file.filename} | "
            f"chunks={result['chunks_added']}"
        )

        # ----------------------------------------------------
        # RETURN RESULT TO FRONTEND
        # ----------------------------------------------------

        return {
            "success": True,
            "filename": result["document_name"],
            "chunks_added": result["chunks_added"],
            "parents_added": result["parents_added"],
            "total_chunks": result["total_chunks"],
        }

    except HTTPException:
        raise

    except Exception as exc:

        logging.exception(
            f"Document ingestion failed: "
            f"{file.filename}"
        )

        print()
        print(
            f"[api] INGESTION ERROR: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"Document ingestion failed: {str(exc)}"
            )
        )

    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            os.remove(
                temp_path
            )


# ============================================================
# CHAT - NON STREAMING
# ============================================================

@app.post("/api/rag/chat")
def rag_chat(
    request: ChatRequest
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # --------------------------------------------------------
    # MODERATION
    # --------------------------------------------------------

    moderation = moderate_text(
        request.question
    )

    if moderation["blocked"]:

        return blocked_response(
            moderation["reason"]
        )

    request.question = moderation[
        "cleaned_text"
    ]

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    history = sessions.get(
        request.session_id,
        []
    )

    print()
    print(
        f"[api] /api/rag/chat "
        f"question: {request.question}"
    )

    # --------------------------------------------------------
    # REWRITE
    # --------------------------------------------------------

    standalone_question = (
        gemini_module.rewrite_question(
            request.question,
            history
        )
    )

    rewritten_flag = (
        standalone_question
        if standalone_question.strip()
        != request.question.strip()
        else None
    )

    if rewritten_flag:

        print(
            f"[api] rewritten question: "
            f"{standalone_question}"
        )

    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    result = rag_pipeline.retrieve(
        standalone_question
    )

    documents = result[
        "documents"
    ]

    reranked_results = result[
        "reranked_results"
    ]

    # --------------------------------------------------------
    # GENERATION
    # --------------------------------------------------------

    answer = gemini_module.generate_answer(
        question=standalone_question,
        documents=documents,
        chat_history=history,
    )

    # --------------------------------------------------------
    # SOURCES + IMAGES
    # --------------------------------------------------------

    sources_string = format_sources_string(
        documents
    )

    image_paths = extract_image_paths(
        reranked_results
    )

    # --------------------------------------------------------
    # SAVE HISTORY
    # --------------------------------------------------------

    history.append(
        ("Human", request.question)
    )

    history.append(
        ("AI", answer)
    )

    sessions[
        request.session_id
    ] = history

    return {
        "answer": answer,
        "sources": sources_string,
        "rewritten_question": rewritten_flag,
        "images": image_paths,
    }


# ============================================================
# STREAMING TEXT CHAT
# ============================================================

@app.post("/api/rag/chat/stream")
def rag_chat_stream(
    request: ChatRequest
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # --------------------------------------------------------
    # MODERATION
    # --------------------------------------------------------

    moderation = moderate_text(
        request.question
    )

    if moderation["blocked"]:

        def blocked_stream():

            yield (
                "event: meta\n"
                f"data: {json.dumps({'sources': '', 'rewritten_question': None, 'images': []})}\n\n"
            )

            yield (
                "event: text_chunk\n"
                f"data: {json.dumps({'text': moderation['reason']})}\n\n"
            )

            yield (
                "event: done\n"
                f"data: {json.dumps({'answer': moderation['reason']})}\n\n"
            )

        return StreamingResponse(
            blocked_stream(),
            media_type="text/event-stream"
        )

    request.question = moderation[
        "cleaned_text"
    ]

    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    history = sessions.get(
        request.session_id,
        []
    )

    # --------------------------------------------------------
    # REWRITE
    # --------------------------------------------------------

    standalone_question = (
        gemini_module.rewrite_question(
            request.question,
            history
        )
    )

    rewritten_flag = (
        standalone_question
        if standalone_question.strip()
        != request.question.strip()
        else None
    )

    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    result = rag_pipeline.retrieve(
        standalone_question
    )

    documents = result[
        "documents"
    ]

    reranked_results = result[
        "reranked_results"
    ]

    sources_string = format_sources_string(
        documents
    )

    image_paths = extract_image_paths(
        reranked_results
    )

    # --------------------------------------------------------
    # STREAM
    # --------------------------------------------------------

    def event_stream():

        meta = {
            "sources": sources_string,
            "rewritten_question": rewritten_flag,
            "images": image_paths,
        }

        yield (
            "event: meta\n"
            f"data: {json.dumps(meta)}\n\n"
        )

        full_answer = []

        for piece in (
            gemini_module.generate_answer_stream(
                question=standalone_question,
                documents=documents,
                chat_history=history,
            )
        ):

            full_answer.append(
                piece
            )

            yield (
                "event: text_chunk\n"
                f"data: {json.dumps({'text': piece})}\n\n"
            )

        answer = "".join(
            full_answer
        )

        history.append(
            ("Human", request.question)
        )

        history.append(
            ("AI", answer)
        )

        sessions[
            request.session_id
        ] = history

        yield (
            "event: done\n"
            f"data: {json.dumps({'answer': answer})}\n\n"
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream"
    )


# ============================================================
# VOICE CHAT
# ============================================================

@app.post("/api/rag/chat/voice")
def rag_chat_voice(
    request: ChatRequest
):

    if not request.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    # --------------------------------------------------------
    # MODERATION
    # --------------------------------------------------------

    moderation = moderate_text(
        request.question
    )

    if moderation["blocked"]:

        logging.info(
            "Voice chat request blocked"
        )

        def blocked_stream():

            yield (
                "event: meta\n"
                f"data: {json.dumps({'sources': '', 'rewritten_question': None, 'images': []})}\n\n"
            )

            yield (
                "event: text_chunk\n"
                f"data: {json.dumps({'text': moderation['reason']})}\n\n"
            )

            yield (
                "event: done\n"
                f"data: {json.dumps({'answer': moderation['reason']})}\n\n"
            )

        return StreamingResponse(
            blocked_stream(),
            media_type="text/event-stream"
        )

    request.question = moderation[
        "cleaned_text"
    ]

    history = sessions.get(
        request.session_id,
        []
    )

    print()
    print(
        f"[api] /api/rag/chat/voice "
        f"question: {request.question}"
    )

    request_start = time.time()

    logging.info(
        f"Voice chat request received | "
        f"question={request.question}"
    )

    # --------------------------------------------------------
    # REWRITE
    # --------------------------------------------------------

    standalone_question = (
        gemini_module.rewrite_question(
            request.question,
            history
        )
    )

    rewritten_flag = (
        standalone_question
        if standalone_question.strip()
        != request.question.strip()
        else None
    )

    # --------------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------------

    retrieval_start = time.time()

    result = rag_pipeline.retrieve(
        standalone_question
    )

    retrieval_time = (
        time.time()
        - retrieval_start
    )

    documents = result[
        "documents"
    ]

    reranked_results = result[
        "reranked_results"
    ]

    logging.info(
        f"Retrieval completed | "
        f"time={retrieval_time:.2f}s | "
        f"docs_found={len(documents)}"
    )

    sources_string = format_sources_string(
        documents
    )

    image_paths = extract_image_paths(
        reranked_results
    )

    # --------------------------------------------------------
    # EVENT STREAM
    # --------------------------------------------------------

    def event_stream():

        # ----------------------------------------------------
        # META
        # ----------------------------------------------------

        meta = {
            "sources": sources_string,
            "rewritten_question": rewritten_flag,
            "images": image_paths,
        }

        yield (
            "event: meta\n"
            f"data: {json.dumps(meta)}\n\n"
        )

        # ----------------------------------------------------
        # GENERATION
        # ----------------------------------------------------

        full_answer = []

        sentence_buffer = ""

        generation_start = time.time()

        for piece in (
            gemini_module.generate_answer_stream(
                question=standalone_question,
                documents=documents,
                chat_history=history,
            )
        ):

            full_answer.append(
                piece
            )

            # Send text immediately
            yield (
                "event: text_chunk\n"
                f"data: {json.dumps({'text': piece})}\n\n"
            )

            # Add to sentence buffer
            sentence_buffer += piece

            sentences, sentence_buffer = (
                extract_complete_sentences(
                    sentence_buffer
                )
            )

            # ------------------------------------------------
            # TTS
            # ------------------------------------------------

            if request.voice:

                for sentence in sentences:

                    try:

                        tts_resp = requests.post(
                            TTS_SERVICE_URL,
                            json={
                                "text": sentence
                            },
                            timeout=120,
                        )

                        if tts_resp.status_code == 200:

                            audio_b64 = (
                                base64.b64encode(
                                    tts_resp.content
                                ).decode("utf-8")
                            )

                            yield (
                                "event: audio_chunk\n"
                                f"data: {json.dumps({'audio': audio_b64})}\n\n"
                            )

                        else:

                            print(
                                f"[api] TTS returned "
                                f"status "
                                f"{tts_resp.status_code}"
                            )

                    except requests.exceptions.RequestException as e:

                        print(
                            f"[api] TTS request failed: {e}"
                        )

        # ----------------------------------------------------
        # FINAL SENTENCE
        # ----------------------------------------------------

        if (
            request.voice
            and sentence_buffer.strip()
        ):

            try:

                tts_resp = requests.post(
                    TTS_SERVICE_URL,
                    json={
                        "text": sentence_buffer.strip()
                    },
                    timeout=120,
                )

                if tts_resp.status_code == 200:

                    audio_b64 = (
                        base64.b64encode(
                            tts_resp.content
                        ).decode("utf-8")
                    )

                    yield (
                        "event: audio_chunk\n"
                        f"data: {json.dumps({'audio': audio_b64})}\n\n"
                    )

            except requests.exceptions.RequestException as e:

                print(
                    f"[api] TTS request failed: {e}"
                )

        # ----------------------------------------------------
        # FINISH
        # ----------------------------------------------------

        generation_time = (
            time.time()
            - generation_start
        )

        answer = "".join(
            full_answer
        )

        # ----------------------------------------------------
        # SAVE HISTORY
        # ----------------------------------------------------

        history.append(
            ("Human", request.question)
        )

        history.append(
            ("AI", answer)
        )

        sessions[
            request.session_id
        ] = history

        total_time = (
            time.time()
            - request_start
        )

        logging.info(
            f"Voice chat request completed | "
            f"total_time={total_time:.2f}s | "
            f"retrieval={retrieval_time:.2f}s | "
            f"generation={generation_time:.2f}s"
        )

        # ----------------------------------------------------
        # DONE
        # ----------------------------------------------------

        yield (
            "event: done\n"
            f"data: {json.dumps({'answer': answer})}\n\n"
        )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================
# TRANSCRIPTION
# ============================================================

@app.post("/api/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No audio file provided."
        )

    allowed_extensions = {
        ".wav",
        ".mp3",
        ".m4a",
        ".webm",
        ".ogg",
        ".mp4"
    }

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported audio format: "
                f"{extension}"
            )
        )

    temp_path = None

    try:

        audio_bytes = await file.read()

        if not audio_bytes:

            raise HTTPException(
                status_code=400,
                detail="Audio file is empty."
            )

        # ----------------------------------------------------
        # TEMP AUDIO FILE
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension
        ) as f:

            f.write(
                audio_bytes
            )

            temp_path = f.name

        # ----------------------------------------------------
        # TRANSCRIBE
        # ----------------------------------------------------

        result = (
            transcription_service.transcribe(
                temp_path
            )
        )

        # ----------------------------------------------------
        # MODERATION
        # ----------------------------------------------------

        moderation = moderate_text(
            result["text"]
        )

        return {
            "success": True,
            "text": moderation[
                "cleaned_text"
            ],
            "language": result[
                "language"
            ],
            "language_probability": result[
                "language_probability"
            ],
            "moderated": bool(
                moderation["flagged"]
            ),
        }

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Transcription failed: "
                f"{str(exc)}"
            )
        )

    finally:

        if (
            temp_path
            and os.path.exists(temp_path)
        ):

            os.remove(
                temp_path
            )