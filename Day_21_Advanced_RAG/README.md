# Day 22 — STT Architecture & Whisper Integration

## Phase 4 — Voice Integration + Deployment

Day 22 extends the enterprise RAG system developed in Day 21 by adding
Speech-to-Text (STT) capabilities.

The system allows users to either type a question or speak through the
browser microphone. Voice input is recorded using the browser's
MediaRecorder API, sent to the FastAPI backend, transcribed using
faster-whisper, and inserted into the existing RAG chat input.

---

## Objective

The objectives of Day 22 are:

- Understand Speech-to-Text architecture.
- Understand Whisper's encoder-decoder Transformer architecture.
- Compare Whisper with other STT technologies.
- Capture microphone audio in a React frontend.
- Send recorded audio to FastAPI.
- Perform server-side transcription using faster-whisper.
- Automatically place the transcript into the chat input.
- Preserve the existing Day 21 RAG pipeline.
- Support both text and voice input.
- Provide recording and transcription states.

---

# 1. System Architecture

The Day 22 voice pipeline is:

```text
User
 │
 ├─────────────── Text Input ───────────────┐
 │                                          │
 │                                          ▼
 │                                    Chat Input
 │                                          │
 │                                          ▼
 │                                    /api/rag/chat
 │                                          │
 │                                          ▼
 │                                    RAG Pipeline
 │                                          │
 │                                          ▼
 │                                         LLM
 │                                          │
 │                                          ▼
 │                                        Answer
 │
 └────────────── Voice Input
                │
                ▼
          Browser Microphone
                │
                ▼
          MediaRecorder API
                │
                ▼
             Audio Blob
                │
                ▼
       POST /api/transcribe
                │
                ▼
          FastAPI Backend
                │
                ▼
         faster-whisper
                │
                ▼
            Transcript
                │
                ▼
           Chat Input
                │
                ▼
              Ask
                │
                ▼
           /api/rag/chat