# AI Learning Companion

A full-stack, AI-powered educational chat app built around the Week 2
curriculum: React + FastAPI + the Google Gemini API, prompt engineering, streaming,
function calling, session management, and token/cost monitoring.

## What's inside

```
ai-tutor-app/
├── backend/
│   ├── main.py                  # FastAPI app: chat, streaming, sessions, tools
│   ├── api_comparison_demo.py   # generate_content vs. stateful chats session, side by side
│   ├── requirements.txt
│   └── .env.example
└── client/                      # React + Vite + Tailwind
    └── src/
        ├── App.jsx
        ├── api.js                # REST + SSE streaming client
        └── components/
            ├── Sidebar.jsx
            ├── ChatMessage.jsx
            ├── MessageInput.jsx
            ├── TypingIndicator.jsx
            ├── PersonaSelector.jsx
            └── StatsBar.jsx
```

## Setup

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then paste your real GEMINI_API_KEY into .env
uvicorn main:app --reload --port 8000
```

Swagger UI (auto-generated docs) is at `http://localhost:8000/docs` — use it
to exercise every endpoint directly, including streaming and tool calls.

### Frontend

```bash
cd client
npm install
npm run dev
```

Open `http://localhost:5173`.

## Feature map (curriculum → implementation)

| Concept | Where |
|---|---|
| Gemini client, structured prompt, JSON response | `backend/main.py` — `client.models.generate_content` calls |
| Token metrics + exact USD cost | `calculate_cost()`, returned in every `ChatResponse` and shown live in `StatsBar` |
| Stateless `generate_content` vs. stateful `chats` session | `backend/api_comparison_demo.py` |
| Streaming (`stream=True`) | `POST /api/chat/stream` (SSE) + `streamChat()` in `api.js`, toggled via the "stream" checkbox in the UI |
| Temperature / Top-P / Max Tokens experiments | `POST /api/experiment/sampling` — runs 3 temperature variants on one prompt |
| system / user / assistant roles | Every session's `messages` array in `chat_sessions` |
| Strict JSON-schema output | `POST /api/prompts/structured-json` — API-level `response_format: json_schema` (`strict: true`) against `STUDY_PLAN_SCHEMA`, **plus** local `pydantic` validation (`StudyPlan`) with one automatic retry that feeds the validation error back to the model on deviation. `json_mode` on `/api/chat` (basic `json_object` mode) still exists for lighter-weight cases. |
| Few-shot examples | `FEW_SHOT_EXAMPLES` in `main.py` |
| Production prompt: structured JSON generation | `/api/prompts/structured-json`, reachable from the UI's **Prompt Lab** panel |
| Production prompt: unstructured text parsing | `/api/prompts/text_parsing` (`PRODUCTION_PROMPTS["text_parsing"]`), Prompt Lab |
| Production prompt: code generation | `/api/prompts/code_generation`, Prompt Lab |
| Production prompt: document summarization | `/api/prompts/summarization`, Prompt Lab |
| Function calling vs. JSON mode — documented | Comment block above `PRODUCTION_PROMPTS` in `main.py` (also summarized below) |
| Persona switching (formal / casual / technical) | `PERSONAS` dict + `PersonaSelector.jsx` |
| Function calling: tools, `tool_choice`, JSON schemas | `TOOLS` list in `main.py` |
| 4 tools: time, calculator, mock search, currency | `execute_tool()` |
| Full tool-calling loop, multi-tool chaining | `run_tool_loop()` (up to 4 hops) |
| Edge cases (declined calls, bad args, tool errors) | try/except in `execute_tool`, allow-listed characters for `calculate`, graceful `json.JSONDecodeError` handling |
| FastAPI `/api/chat`, Pydantic schemas | `ChatRequest` / `ChatResponse` in `main.py` |
| In-memory session store | `chat_sessions` dict |
| `GET /api/sessions` with counts | implemented |
| HTTP status codes + structured errors | `HTTPException(400/404/500)` throughout |
| Structured logging (timestamp, session, tokens, latency) | `log_request()` — JSON lines to stdout |
| React + Vite + Tailwind | `client/` |
| `ChatMessage` styling by role | `ChatMessage.jsx` |
| `MessageInput`: Enter-to-send, char counter | `MessageInput.jsx` |
| CORS | `CORSMiddleware` in `main.py` |
| Typing indicator | `TypingIndicator.jsx` |
| Sidebar, session isolation | `Sidebar.jsx`, `session_id` on every request |
| New Chat (`crypto.randomUUID()`) | `handleNewChat()` in `App.jsx` |
| `localStorage` persistence | `loadStore` / `saveStore` in `App.jsx` |
| Auto-generated session titles | `POST /api/sessions/{id}/title` + `maybeTitle()` |
| Copy / regenerate | `ChatMessage.jsx` actions. Regenerate calls `POST /api/chat/regenerate`, which drops the session's last assistant turn server-side and re-runs the completion **without** appending a duplicate user message — see "Regenerate, fixed" below. |
| 5 simultaneous sessions, isolation verified | `backend/test_session_isolation.py` — automated test (mocks the Gemini call, exercises the real FastAPI/session code) that creates 5 sessions, interleaves messages across them, and asserts zero cross-contamination of history, IDs, or message counts. Run it yourself: `cd backend && python3 -m pytest test_session_isolation.py -v` |

## Function calling vs. JSON mode

| | JSON mode | Function calling |
|---|---|---|
| **What it does** | Constrains the model's own reply to valid JSON / a defined schema | Lets the model call *your* code to get information or take an action, then reason over the result |
| **Use when** | The whole answer IS the structured data (e.g. "return a study plan as JSON") | The model needs something it doesn't know (time, a calculation, a DB row) before it can answer |
| **In this project** | `/api/prompts/structured-json` | `run_tool_loop()`, `/api/chat` with `use_tools: true` |

They're complementary, not competing — a tool's result can itself be JSON that the model later formats into a JSON reply, but most single tasks only need one of the two.

## Regenerate, fixed

The first pass of this app had a bug: "regenerate" resent the last user message through the normal chat path, which (a) appended a **second**, duplicate user bubble in the UI, and (b) appended a duplicate user turn into the backend's session history on every retry, bloating context and cost. It's fixed by giving regenerate its own endpoint that only replaces the trailing assistant turn:

```
POST /api/chat/regenerate  { "session_id": "..." }
```

Server-side, if the session's last message is an assistant reply it's popped, the completion is re-run against the *existing* history (no new user message appended), and the new reply replaces the old one — both in `chat_sessions` and in the frontend's local session state.

## Design notes

The UI leans into a "desk lamp at night" motif — deep navy panels, a warm
amber accent standing in for the lamp's glow, serif headings for a studious
feel, and monospace readouts for token/cost/latency so the "engineering
under the hood" of the app stays visible while you study.

## Known limitations (by design, for a Week-2 scope)

- Sessions live in server memory (`chat_sessions` dict) and are lost on
  backend restart. `localStorage` on the frontend preserves the *sidebar
  list and message history for display*, but continuing a conversation
  after a backend restart will start a fresh context server-side. A
  production version would move `chat_sessions` to Redis/Postgres.
- `calculate` uses a character allow-list + `eval` in an empty builtins
  namespace for simplicity; swap in a real expression parser (e.g. `asteval`)
  before shipping this beyond a classroom demo.
