# Deployment Guide — RAG + Whisper STT + XTTS v2 TTS Stack

## 0. Project structure

```
.
├── backend/
│   ├── Dockerfile              # build context = backend/
│   ├── requirements.txt
│   ├── .dockerignore
│   ├── .env.example            # copy to backend/.env, fill in real values
│   ├── cors_config_reference.py
│   ├── scripts/
│   │   └── warm_models.py      # runs at BUILD time, caches model weights
│   └── app/
│       └── main.py             # FastAPI entrypoint: /health, CORS, STT/RAG/TTS routes
├── frontend/
│   ├── Dockerfile               # only used if self-hosting; skip for Vercel
│   ├── nginx.conf
│   ├── .dockerignore
│   └── .env.example            # copy to frontend/.env.local (Vite) or .env (CRA)
├── docker-compose.yml           # local full-stack test only, not the real deployment
└── DEPLOYMENT_GUIDE.md          # this file
```

`app/main.py` is a working skeleton, not your finished app — it wires up
`/health`, CORS, and model-loading-once-at-startup correctly, but the
`/api/transcribe`, `/api/ask`, and `/api/speak` bodies are placeholders you
replace with your actual Day 23 logic.

## 0a. Local test before deploying anywhere

```bash
cp backend/.env.example backend/.env      # fill in real values
# add http://localhost:5173 to ALLOWED_ORIGINS in backend/.env for local testing
cp frontend/.env.example frontend/.env.local

docker compose up --build
```

Frontend: `http://localhost:5173` · Backend: `http://localhost:8000/health`

Once this works locally, move on to the real two-host deployment below —
`docker-compose.yml` is not used in that deployment; each service is built
and deployed independently.

## 1. Architecture: two separate services

- **Frontend** → Vercel (static build + CDN) — *no Nginx needed here*.
- **Backend** → a host that supports an **always-on container** with real RAM
  (and ideally GPU), *not* Vercel.

Vercel's serverless functions are the wrong fit for the backend for two reasons:
they cold-start per invocation (deadly with multi-GB model weights), and they
don't hold a connection open for streaming — which this app needs for
streamed cloned-voice audio.

## 2. Backend host recommendation

| Option | RAM | GPU | Always-on | WebSockets/streaming | Notes |
|---|---|---|---|---|---|
| **Hugging Face Spaces (Docker SDK)** | 16GB free tier | T4 available (paid) | Yes | Yes — it's a persistent container behind their proxy | Must listen on port `7860` by default (configurable in Space's README metadata `app_port`). Free CPU tier is workable for demos; GPU tier recommended for near-real-time XTTS. |
| **Oracle Cloud Free Tier VM (Ampere A1)** | up to 24GB, 4 OCPU (ARM) | No (free tier) | Yes | Yes — full control, plain Docker/uvicorn | Best if you want full control (SSH, docker-compose, your own reverse proxy/TLS). CPU-only, so expect the CPU latency notes in Section 5. |

**Pick HF Spaces (Docker, GPU tier)** if you want the closest-to-local-GPU
experience and don't mind paying for the GPU hours. **Pick Oracle's free ARM
VM** if you want a genuinely free always-on box and are fine with CPU-only
inference (use `faster-whisper` + int8 quantization, already set up in the
Dockerfile above, to keep CPU latency reasonable).

Either way: do not deploy this backend to Vercel, Netlify functions, AWS
Lambda, or any other serverless platform — none of them keep a container
warm with your models loaded, and most cap function execution/connection
time well below what streamed TTS audio needs.

## 3. Streaming connection type — confirm before you deploy

Check which one your backend actually implements:

- **WebSocket** (e.g. `@app.websocket("/ws/audio")`) — needs a host that
  proxies WebSocket upgrades without terminating them early. Both HF Spaces
  and a plain Oracle VM (behind Caddy/Nginx configured for `Upgrade`/
  `Connection` headers) support this.
- **HTTP chunked / `StreamingResponse`** — works over both hosts too, but if
  you self-host behind Nginx on the Oracle VM, make sure
  `proxy_buffering off;` is set on that location block, or Nginx will buffer
  the whole response before forwarding it, defeating the point of streaming.

Confirm this against your actual `main.py` implementation before deploying —
if you're unsure which one your code uses, grep for `websocket` vs
`StreamingResponse`.

## 4. Deployment steps

### Backend (HF Spaces example)
1. Create a new Space → SDK: **Docker**.
2. Push the contents of the `backend/` folder to the Space's git remote —
   the Space treats the repo root as the Docker build context, and
   `backend/Dockerfile` already assumes that context, so push `backend/`'s
   *contents* to the Space repo root (not the `backend/` folder itself nested
   inside).
3. Set `ALLOWED_ORIGINS`, `OPENAI_API_KEY`, etc. as **Space secrets** (not
   committed `.env` — HF Spaces injects secrets as env vars at runtime).
4. If port 7860 isn't what your app listens on, set `app_port: 8000` in the
   Space's `README.md` YAML front matter, or change the Dockerfile's
   `EXPOSE`/`CMD` port to 7860 to match the default.
5. Wait for the build — model weights are cached during this build step
   (`scripts/warm_models.py`), so first real request after boot is fast.

### Backend (Oracle Cloud VM example)
1. SSH in, install Docker.
2. `cd backend && docker build -t rag-backend .`
3. `docker run -d -p 8000:8000 --env-file .env --restart unless-stopped rag-backend`
4. Put Nginx or Caddy in front for TLS (Let's Encrypt) and to terminate
   `https://` at your domain, forwarding to `localhost:8000` with
   `proxy_buffering off;` for streaming routes.

### Frontend (Vercel)
1. Set `VITE_API_BASE_URL` (or `REACT_APP_API_BASE_URL`) in Vercel's
   **Project → Settings → Environment Variables** to the deployed backend's
   real URL (e.g. `https://your-space.hf.space` or `https://api.yourdomain.com`).
2. Deploy — Vercel handles the build and CDN; no Dockerfile needed here.

### CORS
On the backend, set `ALLOWED_ORIGINS` to the **exact** Vercel domain
(e.g. `https://your-app.vercel.app`), not a wildcard. This is already wired
into `backend/app/main.py` (see also the standalone reference copy at
`backend/cors_config_reference.py`) — it reads `ALLOWED_ORIGINS` from the
environment and splits on commas, so multiple origins are supported as a
comma-separated list. If Vercel generates preview-deploy URLs you also want
to allow, add each exact preview domain to that list, or write a small
origin-regex check for `*.vercel.app` previews specifically — but keep
production locked to the exact domain.

## 5. End-to-end test checklist

Run this against the *deployed* stack, not just locally, before calling it done:

1. **Voice input → Whisper STT**: record/upload audio in the deployed
   frontend, confirm the transcript returned matches Day 23's local test
   transcript for the same clip.
2. **RAG-grounded answer**: confirm retrieved context + generated answer
   match (or are equivalent in substance to) the local Day 23 run for the
   same query — check it isn't silently falling back to non-grounded
   generation (e.g. vector DB failed to load, docs path wrong on the new host).
3. **Streamed cloned-voice audio (XTTS v2)**: confirm audio starts playing
   incrementally rather than only after the full clip finishes generating,
   and that the cloned voice matches the reference speaker sample.
4. **CORS**: open browser dev tools → Network tab, confirm no CORS errors on
   the deployed frontend talking to the deployed backend domain.
5. **Cold start**: restart the backend container and immediately send a
   request — it should respond promptly (proving model caching in the
   Docker build worked) rather than hanging while it downloads weights.

### Expected latency differences: CPU (hosted) vs. local GPU (Day 23)

Be upfront about this in the demo so it doesn't feel "broken":

- **Whisper STT**: `faster-whisper` on CPU (int8) is noticeably slower than a
  local GPU but still generally sub-few-seconds for short clips on a
  `small` model; expect roughly 2–5x the local-GPU transcription time.
- **XTTS v2 synthesis**: this is the biggest gap. XTTS v2 on GPU is close to
  real-time; on CPU it can take several seconds per sentence of output audio.
  This is the step most likely to make a CPU-hosted demo feel sluggish.
  Mitigations: keep responses short, stream sentence-by-sentence as each
  chunk finishes (so the user hears audio start before the whole reply is
  synthesized), and/or pay for the HF Spaces GPU tier if the demo needs to
  feel snappy.
- **RAG retrieval**: embedding + vector search is comparatively cheap and
  shouldn't differ much between CPU and GPU hosts — the LLM generation call
  itself dominates that step's latency and depends on which provider/model
  you're calling, not on this host's hardware.

Net effect: transcription and retrieval should feel close to Day 23; TTS
synthesis is where a CPU host will visibly lag behind local GPU — plan the
demo pacing (or GPU tier) around that.
