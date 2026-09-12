import re
import tempfile
import time
import wave
import logging

from pathlib import Path

import torch
import torchaudio

from fastapi import FastAPI, Response
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from TTS.api import TTS


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    filename="tts_service.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


# ============================================================
# PATHS
# ============================================================

BACKEND_ROOT = Path(__file__).resolve().parent

REFERENCE_VOICE = (
    BACKEND_ROOT
    / "06_voice"
    / "reference_voice.wav"
)

MODEL_NAME = (
    "tts_models/multilingual/multi-dataset/xtts_v2"
)


# ============================================================
# STARTUP
# ============================================================

print()
print("=" * 75)
print("STARTING TTS SERVICE")
print("=" * 75)
print()

print(
    f"[tts] Reference voice: {REFERENCE_VOICE}"
)

print(
    "[tts] Loading XTTS model..."
)

tts_model = TTS(MODEL_NAME)

print(
    "[tts] XTTS model loaded."
)


# ============================================================
# CACHE SPEAKER CONDITIONING
# ============================================================

print()
print("[tts] Computing speaker conditioning latents...")

xtts_model = tts_model.synthesizer.tts_model

gpt_cond_latent, speaker_embedding = (
    xtts_model.get_conditioning_latents(
        audio_path=[str(REFERENCE_VOICE)]
    )
)

print(
    "[tts] Speaker conditioning cached."
)


# ============================================================
# FAST SYNTHESIS
# ============================================================

def synthesize_voice(text: str):

    output = xtts_model.inference(
        text=text,
        language="en",
        gpt_cond_latent=gpt_cond_latent,
        speaker_embedding=speaker_embedding,
        temperature=0.65,
        length_penalty=1.0,
        repetition_penalty=2.0,
        top_k=50,
        top_p=0.8,
    )

    wav = torch.tensor(
        output["wav"]
    ).unsqueeze(0)

    temp_file = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".wav"
    )

    output_path = temp_file.name

    temp_file.close()

    torchaudio.save(
        output_path,
        wav.cpu(),
        24000
    )

    return output_path


# ============================================================
# WAV DURATION
# ============================================================

def get_wav_duration(path):
    import soundfile as sf

    info = sf.info(path)
    return info.duration

# ============================================================
# SENTENCE SPLITTER
# ============================================================

def clean_text_for_speech(text: str):

    cleaned = text

    cleaned = re.sub(
        r"\*\*(.+?)\*\*",
        r"\1",
        cleaned
    )

    cleaned = re.sub(
        r"\*(.+?)\*",
        r"\1",
        cleaned
    )

    cleaned = re.sub(
        r"_(.+?)_",
        r"\1",
        cleaned
    )

    cleaned = re.sub(
        r"^#{1,6}\s*",
        "",
        cleaned,
        flags=re.MULTILINE
    )

    cleaned = re.sub(
        r"^\s*[-+*]\s+",
        "",
        cleaned,
        flags=re.MULTILINE
    )

    cleaned = re.sub(
        r"^\s*\d+[.)]\s*",
        "",
        cleaned,
        flags=re.MULTILINE
    )

    cleaned = cleaned.replace("`", "")

    cleaned = cleaned.replace(
        "|",
        ", "
    )

    cleaned = re.sub(
        r"\n+",
        ". ",
        cleaned
    )

    cleaned = re.sub(
        r"\s{2,}",
        " ",
        cleaned
    )

    return cleaned.strip()


def split_into_sentences(text: str):

    text = clean_text_for_speech(text)

    raw_sentences = re.split(
        r"(?<=[.!?])\s+",
        text.strip()
    )

    raw_sentences = [
        s.strip()
        for s in raw_sentences
        if s.strip()
    ]

    return raw_sentences


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Day 25 XTTS Voice Service"
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
# REQUEST MODEL
# ============================================================

class SpeakRequest(BaseModel):

    text: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "status": "TTS service is running"
    }


# ============================================================
# SPEAK ONE
# ============================================================

@app.post("/api/tts/speak-one")
def speak_one(
    request: SpeakRequest
):

    text = request.text.strip()

    if not text:

        return {
            "error": "Text cannot be empty."
        }

    print()
    print(
        f"[tts] Synthesizing: {text[:100]}..."
    )

    start = time.time()

    output_path = synthesize_voice(text)

    elapsed = time.time() - start

    audio_duration = get_wav_duration(
        output_path
    )

    rtf = (
        elapsed / audio_duration
        if audio_duration > 0
        else 0
    )

    print(
        f"[tts] Done in {elapsed:.2f}s | "
        f"audio={audio_duration:.2f}s | "
        f"RTF={rtf:.2f}"
    )

    logging.info(
        f"TTS | "
        f"text_len={len(text)} | "
        f"synth_time={elapsed:.2f}s | "
        f"audio_duration={audio_duration:.2f}s | "
        f"RTF={rtf:.2f}"
    )

    with open(
        output_path,
        "rb"
    ) as f:

        audio_bytes = f.read()

    return Response(
        content=audio_bytes,
        media_type="audio/wav"
    )


# ============================================================
# STREAMING TTS
# ============================================================

@app.post("/api/tts/speak-stream")
def speak_stream(
    request: SpeakRequest
):

    text = request.text.strip()

    if not text:

        return {
            "error": "Text cannot be empty."
        }

    sentences = split_into_sentences(
        text
    )

    print()
    print(
        f"[tts] Streaming "
        f"{len(sentences)} sentence(s)"
    )

    def audio_chunk_generator():

        for i, sentence in enumerate(
            sentences,
            start=1
        ):

            start = time.time()

            print(
                f"[tts] Chunk {i}: "
                f"{sentence[:70]}..."
            )

            output_path = synthesize_voice(
                sentence
            )

            elapsed = (
                time.time() - start
            )

            audio_duration = (
                get_wav_duration(
                    output_path
                )
            )

            rtf = (
                elapsed / audio_duration
                if audio_duration > 0
                else 0
            )

            print(
                f"[tts] Chunk {i} ready | "
                f"{elapsed:.2f}s | "
                f"audio={audio_duration:.2f}s | "
                f"RTF={rtf:.2f}"
            )

            with open(
                output_path,
                "rb"
            ) as f:

                audio_bytes = f.read()

            size_header = len(
                audio_bytes
            ).to_bytes(
                4,
                "big"
            )

            yield size_header
            yield audio_bytes

    return StreamingResponse(
        audio_chunk_generator(),
        media_type="application/octet-stream"
    )