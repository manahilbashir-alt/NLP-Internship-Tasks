# 🎙️ Day 23 — Voice RAG with Streaming TTS & Voice Cloning

> **NLP Internship — Day 23 Project**

An end-to-end **Voice-enabled Retrieval-Augmented Generation (RAG)** application that combines speech recognition, document retrieval, LLM-based response generation, zero-shot voice cloning, and streaming text-to-speech into a conversational AI system.

---

## 📌 Project Overview

This project extends a traditional RAG pipeline into a **voice-based conversational assistant**.

The user can speak a question through a microphone. The system transcribes the speech using **Whisper**, retrieves relevant information from the indexed documents, generates an answer using **Google Gemini**, and converts the response into speech using **Coqui XTTS v2** with a reference voice.

The application is designed to provide a more natural conversational experience by supporting **streaming TTS**, allowing generated speech to be processed in smaller chunks instead of waiting for the complete response.

### End-to-End Pipeline

```text
┌──────────────────┐
│   User Speech    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│   Whisper STT    │
│ Speech → Text    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  RAG Retrieval   │
│ FAISS + BM25     │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  RRF + Reranker  │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  Google Gemini   │
│ Answer Generation│
└────────┬─────────┘
         ↓
┌──────────────────┐
│    XTTS v2       │
│ Voice Cloning    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Streaming Audio  │
└────────┬─────────┘
         ↓
┌──────────────────┐
│  Voice Response  │
└──────────────────┘
```

---

## 🎯 Objectives

The main objectives of this project are:

* Understand the architecture of modern neural TTS systems.
* Study the **XTTS v2** voice-cloning pipeline.
* Integrate speech-to-text into an existing RAG application.
* Use a reference recording for zero-shot speaker conditioning.
* Generate RAG responses using Google Gemini.
* Implement sentence-level / chunk-based streaming TTS.
* Reduce **Time-to-First-Audio (TTFA)**.
* Build a microphone-based conversational interface.
* Integrate text and audio responses into the React frontend.
* Evaluate the latency bottlenecks of the complete voice pipeline.

---

# 🧠 System Architecture

The application consists of three primary components.

### 1. Speech & RAG Backend

Responsible for:

* Speech-to-text
* Document ingestion
* Retrieval
* Reranking
* Context construction
* Gemini response generation

**Port:** `8003`

### 2. TTS Service

Responsible for:

* XTTS v2 model loading
* Reference voice conditioning
* Voice cloning
* Sentence-level synthesis
* Streaming audio generation

**Port:** `8004`

### 3. React Frontend

Responsible for:

* Microphone recording
* User interaction
* Transcription display
* Response rendering
* Audio playback

**Development server:** Vite

---

# 🔊 XTTS v2 Voice Cloning

The project uses:

```text
tts_models/multilingual/multi-dataset/xtts_v2
```

XTTS v2 supports **zero-shot voice cloning**, where a short reference recording is used to condition the generated speech.

### TTS Processing Pipeline

```text
Input Text
    ↓
Text Normalization
    ↓
Text / Phoneme Representation
    ↓
Speaker Conditioning
    ↑
Reference Voice
    ↓
Acoustic Generation
    ↓
Neural Vocoder
    ↓
Generated Speech
```

The reference recording provides the speaker characteristics required to generate speech resembling the target voice.

---

# 🎤 Reference Voice

The reference voice is stored at:

```text
backend/06_voice/reference_voice.wav
```

The recording is converted to a TTS-compatible WAV format:

| Property      | Value          |
| ------------- | -------------- |
| Format        | WAV            |
| Sample Rate   | 24,000 Hz      |
| Channels      | Mono           |
| Sample Format | 16-bit PCM     |
| Duration      | ~13.85 seconds |

The reference file was validated using `soundfile` before being supplied to XTTS v2.

---

# 🔎 RAG Pipeline

The project uses a hybrid retrieval architecture combining semantic and lexical search.

```text
User Question
      │
      ├───────────────┐
      ↓               ↓
 Dense Retrieval    BM25 Retrieval
      │               │
      └───────┬───────┘
              ↓
        RRF Fusion
              ↓
     Cross-Encoder Reranking
              ↓
       Parent Expansion
              ↓
       Relevant Context
              ↓
        Google Gemini
              ↓
        Final Answer
```

### Retrieval Components

* **FAISS** — dense vector retrieval
* **BM25** — lexical retrieval
* **Reciprocal Rank Fusion (RRF)** — combines retrieval results
* **Cross-Encoder** — reranks candidate passages
* **Parent Expansion** — restores broader document context

During testing, the live retrieval system successfully loaded:

```text
FAISS vectors:       820
BM25 child chunks:   820
Parent documents:    271
```

---

# 📄 Document Ingestion

Uploaded PDF documents are processed through the following pipeline:

```text
PDF
 ↓
Document Parsing
 ↓
Structured Markdown
 ↓
Document Elements
 ↓
Hierarchical Chunking
 ↓
Embeddings
 ↓
FAISS Index
 ↓
BM25 Index
```

The ingestion endpoint is:

```text
POST /api/rag/ingest
```

Newly uploaded documents are incorporated into the live retrieval system.

---

# 🗣️ Speech-to-Text

The project uses **Whisper** for speech recognition.

The voice input follows:

```text
Microphone
    ↓
Recorded Audio
    ↓
Whisper
    ↓
Detected Language
    ↓
Transcribed Question
```

Example:

```text
Audio:
"What is S.M.I.N.?"

        ↓

Transcript:
"What is S.M.I.N.?"
```

---

# 🤖 Response Generation

After transcription, the question is passed to the RAG pipeline.

```text
Transcribed Question
        ↓
Hybrid Retrieval
        ↓
RRF Fusion
        ↓
Cross-Encoder Reranking
        ↓
Relevant Context
        ↓
Google Gemini
        ↓
Generated Answer
```

The generated answer is then passed to XTTS v2 for speech synthesis.

---

# ⚡ Streaming TTS

A conventional TTS pipeline waits for the complete response:

```text
Question
   ↓
RAG
   ↓
Complete Gemini Response
   ↓
Complete TTS Generation
   ↓
Audio Playback
```

This can result in a noticeable delay before the user hears anything.

The streaming implementation instead processes the response incrementally:

```text
Gemini Response
      ↓
┌───────────────┐
│   Sentence 1  │ → TTS → 🔊
└───────────────┘
      ↓
┌───────────────┐
│   Sentence 2  │ → TTS → 🔊
└───────────────┘
      ↓
┌───────────────┐
│   Sentence 3  │ → TTS → 🔊
└───────────────┘
```

### Primary Goal

The main optimization target is:

**Time-to-First-Audio (TTFA)**

Instead of waiting for all speech to be synthesized, the system can begin playback once the first audio chunk is available.

---

# 🌐 API Services

## RAG / STT API

```text
http://127.0.0.1:8003
```

Important endpoints include:

| Endpoint                   | Purpose               |
| -------------------------- | --------------------- |
| `GET /`                    | API health check      |
| `POST /api/transcribe`     | Speech-to-text        |
| `POST /api/rag/ingest`     | PDF ingestion         |
| `POST /api/rag/chat/voice` | Voice-based RAG query |

---

## TTS API

```text
http://127.0.0.1:8004
```

| Endpoint                     | Purpose                      |
| ---------------------------- | ---------------------------- |
| `GET /`                      | TTS service health check     |
| `POST /api/tts/speak`        | Full-response TTS            |
| `POST /api/tts/speak-one`    | Single-sentence synthesis    |
| `POST /api/tts/speak-stream` | Streaming sentence-level TTS |

---

# 🖥️ Frontend

The frontend is implemented using:

* React
* Vite
* JavaScript
* Browser MediaRecorder API

The interface provides:

* 🎤 Microphone input
* 🔴 Recording state
* 📝 Transcription
* 💬 RAG response bubble
* 🔊 Audio playback
* ⚡ Streaming voice response

---

# 📁 Project Structure

```text
Day_23_Voice_RAG/
│
├── backend/
│   │
│   ├── api.py
│   ├── tts_api.py
│   ├── .env
│   │
│   ├── 06_voice/
│   │   ├── 01_speech_to_text.py
│   │   ├── 02_convert_to_wav.py
│   │   ├── 03_content_filter.py
│   │   └── reference_voice.wav
│   │
│   ├── data/
│   └── ...
│
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── vite.config.js
│   └── ...
│
├── docs/
│
└── README.md
```

---

# ⚙️ Installation & Setup

## Prerequisites

Make sure the following are installed:

* Python 3.11
* Node.js
* npm
* FFmpeg
* Git

---

## Backend Setup

Navigate to the backend:

```powershell
cd D:\NLP-Internship\Day_23_Voice_RAG\backend
```

Activate the virtual environment if required:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

Configure the environment variables in:

```text
backend/.env
```

Required API configuration includes the Google Gemini API key.

> Keep API keys private and never commit `.env` to GitHub.

---

# ▶️ Running the Application

The application uses **three independent terminals**.

### Terminal 1 — RAG Backend

```powershell
cd D:\NLP-Internship\Day_23_Voice_RAG\backend
uvicorn api:app --reload --port 8003
```

### Terminal 2 — TTS Backend

```powershell
cd D:\NLP-Internship\Day_23_Voice_RAG\backend
uvicorn tts_api:app --reload --port 8004
```

### Terminal 3 — React Frontend

```powershell
cd D:\NLP-Internship\Day_23_Voice_RAG\frontend
npm run dev
```

The frontend can then be opened using the URL displayed by Vite.

---

# 🔄 Complete Voice Interaction

A complete interaction follows:

```text
┌─────────────────────────┐
│ User speaks into Mic    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Whisper Speech-to-Text  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Hybrid RAG Retrieval    │
│ FAISS + BM25 + RRF      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Cross-Encoder Reranking │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Google Gemini           │
│ Answer Generation       │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ XTTS v2                 │
│ Voice Cloning           │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│ Streaming Audio         │
└────────────┬────────────┘
             ↓
        🔊 Playback
```

---

# 📊 Performance & Latency

Voice interaction latency is influenced by several stages:

```text
Total Latency
=
STT
+
Retrieval
+
LLM Generation
+
TTS
+
Audio Playback
```

The major latency-sensitive stages are:

| Stage     | Description                      |
| --------- | -------------------------------- |
| STT       | Converts user speech to text     |
| Retrieval | Finds relevant document context  |
| LLM       | Generates the answer             |
| TTS       | Converts answer text into speech |
| Playback  | Starts audio output              |

### Streaming Optimization

The most important metric for streaming TTS is:

```text
Time-to-First-Audio (TTFA)
```

It measures the time between submitting the request and receiving the first playable audio chunk.

Streaming aims to improve perceived responsiveness even when total synthesis time remains similar.

---

# 🧪 Testing Status

| Component               | Status         |
| ----------------------- | -------------- |
| FastAPI backend         | ✅ Working      |
| Whisper STT             | ✅ Working      |
| PDF ingestion           | ✅ Working      |
| FAISS retrieval         | ✅ Working      |
| BM25 retrieval          | ✅ Working      |
| RRF fusion              | ✅ Working      |
| Cross-encoder reranking | ✅ Working      |
| Gemini generation       | ✅ Working      |
| XTTS v2                 | ✅ Working      |
| Reference voice         | ✅ Working      |
| Voice cloning           | ✅ Working      |
| Sentence-level TTS      | ✅ Working      |
| Streaming TTS endpoint  | ✅ Implemented  |
| React frontend          | ✅ Working      |
| Microphone input        | ✅ Working      |
| Voice RAG flow          | ✅ Tested       |
| Latency benchmarking    | 🔄 In progress |

---

# 🛠️ Troubleshooting

### TTS cannot read the reference voice

Verify the file:

```text
backend/06_voice/reference_voice.wav
```

Test it with:

```powershell
python -c "import soundfile as sf; x,sr=sf.read('reference_voice.wav'); print('OK'); print('Sample rate:',sr); print('Shape:',x.shape)"
```

The reference audio should be a valid WAV file.

---

### Backend does not start

Run:

```powershell
cd D:\NLP-Internship\Day_23_Voice_RAG\backend
uvicorn api:app --reload --port 8003
```

Check the terminal for startup errors.

---

### TTS service does not start

Run:

```powershell
cd D:\NLP-Internship\Day_23_Voice_RAG\backend
uvicorn tts_api:app --reload --port 8004
```

XTTS v2 may take some time to load during startup.

---

### Frontend cannot communicate with backend

Verify that:

```text
Frontend → Port 5173
RAG API  → Port 8003
TTS API  → Port 8004
```

are all running simultaneously.

Also verify the frontend API base URL and CORS configuration.

---

# 🔐 Security Notes

* API keys must be stored in `.env`.
* `.env` should be excluded from version control.
* Reference voice recordings should not be publicly exposed.
* Do not commit private credentials or sensitive audio recordings to the repository.

Recommended `.gitignore` entries:

```text
.env
.venv/
__pycache__/
*.pyc
*.log
```

---

# 📚 Key Concepts Learned

This project provided practical experience with:

* Retrieval-Augmented Generation
* Hybrid Information Retrieval
* FAISS
* BM25
* Reciprocal Rank Fusion
* Cross-Encoder Reranking
* Speech-to-Text
* Neural Text-to-Speech
* XTTS v2
* Zero-shot Voice Cloning
* Speaker Conditioning
* Streaming Audio
* FastAPI
* React
* REST APIs
* CORS
* Latency Optimization
* Real-time Voice AI

---

# 🚀 Future Improvements

Potential improvements include:

* True token-level LLM streaming.
* More efficient audio chunk buffering.
* WebSocket-based bidirectional communication.
* Lower-latency TTS models.
* GPU acceleration for inference.
* Voice activity detection (VAD).
* Improved interruption handling.
* Real-time conversational turn-taking.
* More detailed latency benchmarking.
* Production deployment.

---

# ✅ Final Outcome

The Day 23 implementation successfully integrates **voice interaction with the existing RAG system**.

The resulting application combines:

**Whisper + Hybrid RAG + Gemini + XTTS v2 + Voice Cloning + Streaming TTS + React**

to create a conversational Voice RAG pipeline capable of accepting spoken questions and producing knowledge-grounded spoken responses.

---

## 👩‍💻 Internship Project

**Project:** Voice RAG with Streaming TTS & Voice Cloning
**Day:** 23
**Domain:** NLP / Generative AI / Speech AI / RAG
**Frontend:** React + Vite
**Backend:** FastAPI
**LLM:** Google Gemini
**STT:** Whisper
**TTS:** Coqui XTTS v2
**Retrieval:** FAISS + BM25 + RRF
**Language:** Python + JavaScript
