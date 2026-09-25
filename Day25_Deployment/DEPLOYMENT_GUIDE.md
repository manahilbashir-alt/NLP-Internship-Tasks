# Deployment Guide — Day 25 Voice RAG Deployment

## 1. Project Overview

This project is the deployed version of the Day 23 Voice RAG application.

The system includes:

* Retrieval-Augmented Generation (RAG)
* FAISS vector search
* BM25 + dense retrieval
* Reciprocal Rank Fusion (RRF)
* Gemini answer generation
* Whisper speech-to-text (STT)
* XTTS v2 text-to-speech (TTS)
* Voice cloning
* Conversation/session memory
* React frontend
* Dockerized backend and TTS services

Project location:

```text
D:\Projects\NLP-Internship-Tasks\Day25_Deployment
```

---

## 2. Project Structure

```text
Day25_Deployment/
│
├── backend/
│   ├── 01_ingestion/
│   ├── 02_chunking/
│   ├── 03_embeddings/
│   ├── 04_vector_databases/
│   ├── 05_retrieval/
│   ├── 06_voice/
│   ├── data/
│   ├── evaluation/
│   ├── .dockerignore
│   ├── .env
│   ├── Dockerfile
│   ├── Dockerfile.tts
│   ├── requirements.txt
│   ├── requirements-tts.txt
│   ├── api.py
│   └── tts_api.py
│
├── backend_deployment_skeleton/
│
├── frontend/
│
├── docker-compose.yml
├── .gitignore
└── DEPLOYMENT_GUIDE.md
```

### Important

The actual Day 25 FastAPI backend entrypoint is:

```text
backend/api.py
```

The TTS service entrypoint is:

```text
backend/tts_api.py
```

The old `app/main.py` skeleton is **not** the deployed application.

---

## 3. Deployment Architecture

The final demonstration architecture is:

```text
                    ┌──────────────────────┐
                    │   Vercel Frontend    │
                    │   React Application   │
                    └──────────┬───────────┘
                               │ HTTPS
                               ▼
                    ┌──────────────────────┐
                    │ Cloudflare Quick      │
                    │ Tunnel                │
                    └──────────┬───────────┘
                               │
                               ▼
              ┌─────────────────────────────────┐
              │ Docker FastAPI Backend          │
              │ Port 8000                       │
              │ RAG + Whisper STT               │
              └──────────────┬──────────────────┘
                             │
                             │ HTTP
                             ▼
              ┌─────────────────────────────────┐
              │ Docker XTTS v2 TTS Service      │
              │ Port 8004                       │
              │ Voice cloning / synthesis       │
              └─────────────────────────────────┘
```

### Services

| Service           |  Port | Purpose                         |
| ----------------- | ----: | ------------------------------- |
| Backend           |  8000 | FastAPI, RAG and Whisper STT    |
| TTS               |  8004 | XTTS v2 voice synthesis         |
| Frontend          |  5173 | Local React frontend            |
| Vercel            | HTTPS | Deployed frontend               |
| Cloudflare Tunnel | HTTPS | Temporary public backend access |

---

## 4. Why the Backend Is Not Hosted on Vercel

The frontend is suitable for Vercel because it is a React application.

The backend contains large machine-learning models and requires a persistent process for:

* Whisper STT
* embeddings
* vector retrieval
* RAG processing
* XTTS v2
* voice cloning
* audio processing

Therefore, the FastAPI backend and TTS service run in Docker rather than as Vercel serverless functions.

---

## 5. Docker Configuration

### Backend

The backend Dockerfile uses Python 3.11 and installs the required RAG and voice-processing dependencies.

The backend container runs:

```text
uvicorn api:app --host 0.0.0.0 --port 8000
```

Backend port:

```text
8000
```

### TTS

The TTS Dockerfile contains:

* Coqui TTS 0.22.0
* XTTS v2
* PyTorch
* torchaudio
* FastAPI
* FFmpeg

The TTS container runs:

```text
uvicorn tts_api:app --host 0.0.0.0 --port 8004
```

TTS port:

```text
8004
```

---

## 6. Docker Compose

The project uses Docker Compose to run the backend, TTS and frontend together.

Start the stack:

```powershell
cd D:\Projects\NLP-Internship-Tasks\Day25_Deployment

docker compose up -d
```

Check the containers:

```powershell
docker compose ps
```

Expected services:

```text
day25_deployment-backend-1
day25_deployment-tts-1
day25_deployment-frontend-1
```

The verified deployment had:

```text
backend    Up (healthy)    0.0.0.0:8000->8000/tcp
tts        Up (healthy)    0.0.0.0:8004->8004/tcp
frontend   Up              0.0.0.0:5173->80/tcp
```

---

## 7. Docker Hub Images

The backend and TTS images were successfully pushed to Docker Hub.

Backend:

```text
manahil4502/day25-backend:latest
```

TTS:

```text
manahil4502/day25-tts:latest
```

Both images were successfully pulled back from Docker Hub and verified.

The images are large because they contain machine-learning dependencies and model-related files.

Approximate sizes:

```text
Backend image: 13.3 GB
TTS image:     15.5 GB
Frontend image: 76.6 MB
```

---

## 8. Local Backend Verification

The backend root endpoint can be tested with:

```powershell
Invoke-WebRequest http://127.0.0.1:8000/ -UseBasicParsing
```

Expected response:

```json
{
  "status": "Day 23 Voice RAG API is running"
}
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 9. RAG Backend Configuration

The deployed backend successfully loaded the RAG pipeline.

Verified configuration included approximately:

```text
FAISS vectors: 820
Metadata records: 820
BM25 searchable children: 820
RRF k: 60
Parent lookup: 271
```

The embedding/retrieval pipeline loaded successfully.

---

## 10. Public Backend Deployment

Because a permanent card-free hosting option with sufficient resources for XTTS v2 was not used for this deployment, a Cloudflare Quick Tunnel was used to expose the Docker backend publicly.

The tunnel was started with:

```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```

The verified public tunnel URL was:

```text
https://moment-this-threshold-industry.trycloudflare.com
```

---

## 11. Cloudflare Quick Tunnel Limitation

The Cloudflare Quick Tunnel is a temporary demonstration/public-access solution.

It is dependent on the local machine.

The backend remains publicly accessible only while:

* Docker is running
* the FastAPI backend is running
* the TTS service is running
* the `cloudflared` process is running
* the laptop is powered on
* the laptop has an active internet connection

The Quick Tunnel URL can change when a new tunnel is created.

Therefore, this should be described as a **temporary demonstration deployment**, not permanent production hosting.

---

## 12. Public Backend Testing

The public root endpoint was tested:

```powershell
Invoke-WebRequest https://moment-this-threshold-industry.trycloudflare.com/ -UseBasicParsing
```

Result:

```text
StatusCode: 200
```

Swagger was also tested:

```powershell
Invoke-WebRequest https://moment-this-threshold-industry.trycloudflare.com/docs -UseBasicParsing
```

Result:

```text
StatusCode: 200
```

This confirmed:

```text
Internet
   ↓
Cloudflare Quick Tunnel
   ↓
Docker Backend
```

was working correctly.

---

## 13. Public RAG API Testing

An initial test using an incomplete request correctly returned HTTP 422 because the API requires:

```text
session_id
question
```

The correct request was:

```powershell
Invoke-WebRequest `
  https://moment-this-threshold-industry.trycloudflare.com/api/rag/chat `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"session_id":"test123","question":"What is supervised learning?"}' `
  -UseBasicParsing
```

Result:

```text
StatusCode: 200
```

The response contained a correct RAG-generated answer about supervised learning.

Therefore the following complete path was verified:

```text
Public HTTPS
      ↓
Cloudflare Tunnel
      ↓
FastAPI Docker Backend
      ↓
RAG Retrieval
      ↓
Answer Generation
```

---

## 14. Vercel Frontend

The React frontend was successfully deployed to Vercel.

Project:

```text
nlp-internship-tasks-wgql
```

Production URL:

```text
https://nlp-internship-tasks-wgql.vercel.app
```

The deployed frontend successfully communicated with the public backend.

The existing working Vercel configuration was retained during final testing.

---

## 15. CORS Configuration

The FastAPI backend contains the required CORS configuration for the deployed Vercel frontend.

The production Vercel domain is included in the allowed origins.

The backend should use explicit allowed origins rather than:

```text
*
```

when credentials or authenticated requests are involved.

---

## 16. End-to-End Voice RAG Pipeline

The final application pipeline is:

```text
User speaks
     ↓
Browser microphone
     ↓
Whisper STT
     ↓
Transcribed question
     ↓
Hybrid RAG retrieval
     ↓
Dense retrieval + BM25
     ↓
RRF fusion
     ↓
Relevant document context
     ↓
Gemini answer generation
     ↓
XTTS v2
     ↓
Generated voice audio
     ↓
React frontend
```

---

## 17. Whisper Speech-to-Text

The backend uses:

```text
Whisper model: small.en
```

The deployed microphone workflow was successfully tested.

Result:

```text
PASS
```

Audio from the browser was successfully processed and converted into text.

---

## 18. RAG Testing

The RAG pipeline was manually evaluated using 11 generated questions.

Topics included:

1. Supervised learning
2. Support Vector Machines
3. Unsupervised learning
4. Supervised vs. unsupervised learning
5. Training sets
6. Examples of supervised learning
7. Classification
8. Regression
9. Supervised learning vs. classification
10. Follow-up contextual question
11. Follow-up question about the earlier difference

Results:

```text
11/11 questions relevant/correct
2/2 follow-up context tests worked
```

Example retrieved source:

```text
MACHINE LEARNING.pdf
```

Relevant pages included:

```text
17
18
19
36
54
60
```

Two evaluation cases had incomplete page metadata, but the retrieved answers themselves were relevant.

---

## 19. Conversation Memory

Conversation/session memory was tested through follow-up questions.

Result:

```text
PASS
```

The application successfully retained previous conversation context and used it when answering follow-up questions.

---

## 20. XTTS v2 Text-to-Speech

The TTS service uses:

```text
XTTS v2
```

The TTS service was successfully connected to the FastAPI backend through Docker networking.

Inside Docker Compose, the backend communicates with:

```text
http://tts:8004/api/tts/speak-one
```

The frontend successfully received generated audio.

Result:

```text
PASS
```

---

## 21. Complete Manual Test Results

| Test                      | Result |
| ------------------------- | ------ |
| Docker backend            | PASS   |
| Docker TTS                | PASS   |
| Docker Compose            | PASS   |
| Docker Hub backend image  | PASS   |
| Docker Hub TTS image      | PASS   |
| Backend health endpoint   | PASS   |
| Swagger                   | PASS   |
| Cloudflare tunnel         | PASS   |
| Public RAG endpoint       | PASS   |
| Vercel frontend           | PASS   |
| Text query                | PASS   |
| Microphone input          | PASS   |
| Whisper STT               | PASS   |
| RAG retrieval             | PASS   |
| Gemini answer             | PASS   |
| XTTS v2 TTS               | PASS   |
| Audio response            | PASS   |
| Conversation memory       | PASS   |
| RAG evaluation            | PASS   |
| End-to-end voice pipeline | PASS   |

---

## 22. Local vs Demonstration Deployment

### Local

```text
React Frontend
      ↓
localhost:5173
      ↓
Docker Backend :8000
      ↓
Docker TTS :8004
```

### Public Demonstration

```text
Vercel Frontend
      ↓
HTTPS
      ↓
Cloudflare Quick Tunnel
      ↓
Laptop Docker Backend :8000
      ↓
Docker TTS :8004
```

---

## 23. Environment Variables

Important model configuration includes:

```text
WHISPER_MODEL_NAME=small.en

XTTS_MODEL_NAME=tts_models/multilingual/multi-dataset/xtts_v2

EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

Docker Compose configures the internal TTS service using:

```text
TTS_SERVICE_URL=http://tts:8004/api/tts/speak-one
```

API keys and other secrets must remain in `.env` and must not be committed to GitHub.

---

## 24. Performance Notes

The current demonstration uses CPU-based Docker inference.

Expected behavior:

* RAG retrieval is comparatively lightweight.
* Whisper CPU inference is slower than GPU inference.
* XTTS v2 is the most computationally expensive component.
* Shorter responses provide a better voice-demo experience.

The complete voice pipeline was successfully tested despite CPU-based inference.

---

## 25. Troubleshooting

### Check Docker containers

```powershell
docker compose ps
```

### Start Docker services

```powershell
docker compose up -d
```

### View backend logs

```powershell
docker compose logs backend --tail 100
```

### View TTS logs

```powershell
docker compose logs tts --tail 100
```

### Restart services

```powershell
docker compose restart
```

### Check Docker installation

```powershell
docker version
```

### Test backend locally

```powershell
Invoke-WebRequest http://127.0.0.1:8000/ -UseBasicParsing
```

### Test the public tunnel

```powershell
Invoke-WebRequest https://YOUR-TUNNEL.trycloudflare.com/ -UseBasicParsing
```

If the public URL stops working, verify:

1. Docker containers are running.
2. Backend port `8000` is available.
3. TTS container is running.
4. The `cloudflared` terminal is still running.
5. The laptop has internet access.

---

## 26. Final Run Commands

From the Day 25 directory:

```powershell
cd D:\Projects\NLP-Internship-Tasks\Day25_Deployment
```

Start Docker:

```powershell
docker compose up -d
```

Check services:

```powershell
docker compose ps
```

Start the public tunnel in a separate terminal:

```powershell
cloudflared tunnel --url http://127.0.0.1:8000
```

Keep the Cloudflare terminal open while demonstrating the application.

---

## 27. Final Deployment Status

The Day 25 deployment has been successfully verified across the complete pipeline:

```text
Vercel
   ↓
Cloudflare Quick Tunnel
   ↓
Docker FastAPI Backend
   ↓
Whisper STT
   ↓
RAG Retrieval
   ↓
Gemini
   ↓
XTTS v2
   ↓
Audio Response
```

The Dockerized backend, TTS service, public API, Vercel frontend, voice input, RAG retrieval, conversation memory and audio response were all tested successfully.

The only deployment limitation is that the current public backend uses a **temporary Cloudflare Quick Tunnel** rather than permanent cloud hosting. The application itself is fully functional and the end-to-end demonstration has been verified.
