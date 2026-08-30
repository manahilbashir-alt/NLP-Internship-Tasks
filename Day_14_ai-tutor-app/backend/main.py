"""
AI Learning Companion — Backend
================================
A FastAPI service that wraps the Google Gemini API to power an educational
chat application. Demonstrates: single-turn vs chat-session usage, streaming,
temperature/top_p experimentation, system/user/model roles, structured JSON
output, few-shot prompting, persona switching, function calling with a
multi-tool agent loop, session management, token/cost tracking, structured
logging, and local moderation of harsh/abusive user tone.

This file is routing + orchestration ONLY. Prompt content (personas,
few-shot examples, production prompt templates, JSON schemas) lives in
`prompts.py`; the abuse/harsh-tone detection and de-escalation logic lives
in `moderation.py`. Keeping those separate from the FastAPI routes means
either one can be edited/tuned without touching request handling.

Run:
    pip install -r requirements.txt
    export GEMINI_API_KEY=AIza...
    uvicorn main:app --reload --port 8000
"""

import os
import json
import time
import uuid
import logging
from datetime import datetime
from typing import Optional, Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field, ValidationError
from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import (
    PERSONAS,
    DEFAULT_PERSONA,
    FEW_SHOT_EXAMPLES,
    PRODUCTION_PROMPTS,
    STUDY_PLAN_SCHEMA,
    TITLE_SYSTEM_PROMPT,
    build_system_instruction,
)
from moderation import check_tone, moderated_response, log_moderation_event

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

load_dotenv()

_gemini_api_key = os.environ.get("GEMINI_API_KEY")
if not _gemini_api_key:
    # Warn, but do NOT crash at import time — genai.Client() raises
    # immediately if api_key is falsy, which would take down the whole
    # uvicorn process before it can even bind to a port. A placeholder
    # key lets the server start; requests will fail with a clear 500
    # error (caught below) instead of the frontend seeing a raw
    # "Failed to fetch" because the server never came up.
    print("WARNING: GEMINI_API_KEY is not set. Set it as an environment "
          "variable before making requests (see .env.example).")

client = genai.Client(api_key=_gemini_api_key or "missing-api-key")
MODEL = "gemini-3.1-flash-lite"

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger("ai-tutor")

app = FastAPI(title="AI Learning Companion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Pricing (USD per 1M tokens) — gemini-3.1-flash-lite, adjust if Google
# changes pricing. Currently free-tier (Gemini API free tier == $0).
# ---------------------------------------------------------------------------

PRICING = {
    "gemini-3.1-flash-lite": {
        "input": 0.0,
        "output": 0.0,
    },
}


def calculate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rates = PRICING.get(model, PRICING["gemini-3.1-flash-lite"])
    cost = (prompt_tokens / 1_000_000) * rates["input"] + \
           (completion_tokens / 1_000_000) * rates["output"]
    return round(cost, 6)


# ---------------------------------------------------------------------------
# NOTE: Personas, few-shot examples, production prompt templates, and the
# structured-output schema all live in prompts.py now, not here — see that
# file. main.py only ever *uses* prompts, it doesn't define them. The
# function-calling-vs-JSON-mode explanation also moved there since it's
# prompt/response-shaping guidance, not routing logic.
# ---------------------------------------------------------------------------


class StudyPlan(BaseModel):
    """Pydantic model used to validate the model's JSON output locally —
    this is the code-side 'handle any deviation' safety net that sits
    behind the API-level response_json_schema constraint."""
    topic: str
    difficulty: Literal["beginner", "intermediate", "advanced"]
    estimated_minutes: int
    steps: list[str]

# ---------------------------------------------------------------------------
# In-memory session store
# ---------------------------------------------------------------------------
# chat_sessions[session_id] = {
#     "title": str, "persona": str, "created_at": iso, "messages": [...],
#     "usage": {"prompt_tokens": int, "completion_tokens": int, "cost": float}
# }
#
# `messages` keeps an OpenAI-flavored shape for storage/display purposes
# (role: system/user/assistant/tool), regardless of the backing model API.
# `build_contents()` below translates it into Gemini's `Content`/`Part`
# format right before each API call. The system-role entry (index 0) is
# never sent as a turn — it's passed as `system_instruction` instead.

chat_sessions: dict[str, dict] = {}


def new_session(persona: str = DEFAULT_PERSONA) -> dict:
    return {
        "title": "New chat",
        "persona": persona,
        "created_at": datetime.utcnow().isoformat(),
        "messages": [{"role": "system", "content": PERSONAS[persona]}],
        "usage": {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0},
    }


def build_contents(messages: list) -> list:
    """Converts our internal OpenAI-flavored message list into a list of
    Gemini `types.Content` objects. Skips the system-role entry (handled
    separately via `system_instruction`)."""
    contents: list[types.Content] = []
    for m in messages:
        role = m["role"]
        if role == "system":
            continue
        if role == "user":
            contents.append(types.Content(
                role="user", parts=[types.Part.from_text(text=m["content"])],
            ))
        elif role == "assistant":
            if m.get("function_calls"):
                parts = [
                    types.Part.from_function_call(name=fc["name"], args=fc["args"] or {})
                    for fc in m["function_calls"]
                ]
                contents.append(types.Content(role="model", parts=parts))
            else:
                contents.append(types.Content(
                    role="model", parts=[types.Part.from_text(text=m.get("content") or "")],
                ))
        elif role == "tool":
            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_function_response(
                    name=m["name"], response={"result": m["content"]},
                )],
            ))
    return contents


# ---------------------------------------------------------------------------
# Tool / function-calling definitions
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "get_current_time",
        "description": "Get the current UTC date and time.",
        "parameters_json_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "calculate",
        "description": "Evaluate a basic arithmetic expression, e.g. '12 * (3 + 4)'.",
        "parameters_json_schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A math expression using + - * / ( ) and numbers only.",
                }
            },
            "required": ["expression"],
        },
    },
    {
        "name": "search_database",
        "description": "Search a mock study-topic database for a short reference note on a subject.",
        "parameters_json_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Topic to look up."}
            },
            "required": ["query"],
        },
    },
    {
        "name": "format_currency",
        "description": "Format a numeric amount as a currency string.",
        "parameters_json_schema": {
            "type": "object",
            "properties": {
                "amount": {"type": "number"},
                "currency": {"type": "string", "description": "ISO code, e.g. USD, EUR"},
            },
            "required": ["amount", "currency"],
        },
    },
]

GEMINI_TOOLS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name=t["name"],
            description=t["description"],
            parameters_json_schema=t["parameters_json_schema"],
        )
        for t in TOOL_SCHEMAS
    ])
]

MOCK_DB = {
    "photosynthesis": "Process by which plants convert light energy into chemical energy (glucose) using CO2 and water, releasing oxygen.",
    "newton's laws": "Three laws describing motion: (1) inertia, (2) F=ma, (3) equal & opposite reactions.",
    "french revolution": "1789-1799 period of radical political/social upheaval in France that ended the monarchy.",
    "big o notation": "Describes the upper-bound growth rate of an algorithm's time or space requirements as input size grows.",
}


def execute_tool(name: str, arguments: dict) -> str:
    """Executes a tool call locally and returns a string result."""
    try:
        if name == "get_current_time":
            return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

        if name == "calculate":
            expr = arguments.get("expression", "")
            allowed = set("0123456789+-*/(). ")
            if not expr or not set(expr).issubset(allowed):
                return json.dumps({"error": "Invalid characters in expression."})
            try:
                result = eval(expr, {"__builtins__": {}}, {})
            except Exception as e:
                return json.dumps({"error": f"Could not evaluate expression: {e}"})
            return json.dumps({"result": result})

        if name == "search_database":
            query = arguments.get("query", "").lower().strip()
            for key, note in MOCK_DB.items():
                if key in query or query in key:
                    return json.dumps({"topic": key, "note": note})
            return json.dumps({"error": f"No entry found for '{query}'."})

        if name == "format_currency":
            amount = arguments.get("amount")
            currency = arguments.get("currency", "USD").upper()
            if amount is None:
                return json.dumps({"error": "Missing amount."})
            symbols = {"USD": "$", "EUR": "\u20ac", "GBP": "\u00a3", "PKR": "Rs "}
            symbol = symbols.get(currency, currency + " ")
            return json.dumps({"formatted": f"{symbol}{amount:,.2f}"})

        return json.dumps({"error": f"Unknown tool '{name}'."})
    except Exception as e:
        return json.dumps({"error": str(e)})


def run_tool_loop(messages: list, system_instruction: str, max_hops: int = 4) -> tuple[list, dict]:
    """
    Full function-calling loop:
    send tools -> model picks function(s) -> execute locally ->
    send result back -> model synthesizes final response.
    Supports chaining multiple tool calls across hops.
    Returns (updated_messages, usage_totals).
    """
    usage_totals = {"prompt_tokens": 0, "completion_tokens": 0}

    for _ in range(max_hops):
        response = client.models.generate_content(
            model=MODEL,
            contents=build_contents(messages),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=GEMINI_TOOLS,
            ),
        )
        um = response.usage_metadata
        if um:
            usage_totals["prompt_tokens"] += um.prompt_token_count or 0
            usage_totals["completion_tokens"] += um.candidates_token_count or 0

        function_calls = response.function_calls
        if not function_calls:
            messages.append({"role": "assistant", "content": response.text or ""})
            break  # model produced a final answer

        messages.append({
            "role": "assistant",
            "content": None,
            "function_calls": [
                {"name": fc.name, "args": dict(fc.args or {})} for fc in function_calls
            ],
        })

        for fc in function_calls:
            result = execute_tool(fc.name, dict(fc.args or {}))
            messages.append({
                "role": "tool",
                "name": fc.name,
                "content": result,
            })

    return messages, usage_totals


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    persona: Literal["formal", "casual", "technical"] = DEFAULT_PERSONA
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    max_tokens: int = Field(default=600, ge=1, le=4000)
    use_tools: bool = False
    json_mode: bool = False
    stream: bool = False


class ChatResponse(BaseModel):
    session_id: str
    reply: str
    usage: dict
    latency_ms: int
    moderated: bool = False


class TitleRequest(BaseModel):
    session_id: str


class RegenerateRequest(BaseModel):
    session_id: str


class ProductionPromptRequest(BaseModel):
    input: str


# ---------------------------------------------------------------------------
# Logging helper
# ---------------------------------------------------------------------------

def log_request(session_id: str, model: str, usage: dict, latency_ms: int, extra: str = ""):
    logger.info(json.dumps({
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "model": model,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "total_tokens": usage.get("prompt_tokens", 0) + usage.get("completion_tokens", 0),
        "cost_usd": usage.get("cost", 0.0),
        "latency_ms": latency_ms,
        "note": extra,
    }))


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"status": "ok", "service": "AI Learning Companion API"}


@app.get("/api/sessions")
def list_sessions():
    return [
        {
            "session_id": sid,
            "title": s["title"],
            "persona": s["persona"],
            "created_at": s["created_at"],
            "message_count": len([m for m in s["messages"] if m["role"] != "system"]),
            "usage": s["usage"],
        }
        for sid, s in chat_sessions.items()
    ]


@app.get("/api/sessions/{session_id}")
def get_session(session_id: str):
    session = chat_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"session_id": session_id, **session}


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found.")
    del chat_sessions[session_id]
    return {"deleted": session_id}


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Non-streaming chat endpoint. Supports tool use and JSON mode."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty.")

    session_id = req.session_id or str(uuid.uuid4())
    is_new = session_id not in chat_sessions
    if is_new:
        chat_sessions[session_id] = new_session(req.persona)

    session = chat_sessions[session_id]
    session["messages"].append({"role": "user", "content": req.message})
    system_instruction = build_system_instruction(session["persona"])

    # --- Tone check, before the message ever reaches the model. -----------
    # Harsh/abusive input never gets forwarded to the API: we short-circuit
    # here with a de-escalation reply, log the event, and skip the model
    # call entirely (zero tokens, zero cost, zero latency).
    tone = check_tone(req.message)
    if tone["flagged"]:
        turn_count = sum(1 for m in session["messages"] if m["role"] == "user")
        reply = moderated_response(tone["reasons"], turn_count)
        session["messages"].append({"role": "assistant", "content": reply})
        logger.info(json.dumps(log_moderation_event(session_id, tone["reasons"])))
        zero_usage = {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}
        return ChatResponse(
            session_id=session_id,
            reply=reply,
            usage=zero_usage,
            latency_ms=0,
            moderated=True,
        )

    start = time.time()
    try:
        if req.use_tools:
            messages_copy = list(session["messages"])
            updated_messages, usage_totals = run_tool_loop(messages_copy, system_instruction)
            session["messages"] = updated_messages
            reply = session["messages"][-1].get("content") or ""
            usage = usage_totals
        else:
            if req.json_mode and "json" not in system_instruction.lower():
                system_instruction += " Always respond ONLY with a valid JSON object."

            config_kwargs = dict(
                system_instruction=system_instruction,
                temperature=req.temperature,
                top_p=req.top_p,
                max_output_tokens=req.max_tokens,
            )
            if req.json_mode:
                config_kwargs["response_mime_type"] = "application/json"

            response = client.models.generate_content(
                model=MODEL,
                contents=build_contents(session["messages"]),
                config=types.GenerateContentConfig(**config_kwargs),
            )
            reply = response.text or ""
            session["messages"].append({"role": "assistant", "content": reply})
            um = response.usage_metadata
            usage = {
                "prompt_tokens": (um.prompt_token_count or 0) if um else 0,
                "completion_tokens": (um.candidates_token_count or 0) if um else 0,
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")

    latency_ms = int((time.time() - start) * 1000)
    cost = calculate_cost(MODEL, usage["prompt_tokens"], usage["completion_tokens"])
    session["usage"]["prompt_tokens"] += usage["prompt_tokens"]
    session["usage"]["completion_tokens"] += usage["completion_tokens"]
    session["usage"]["cost"] = round(session["usage"]["cost"] + cost, 6)

    full_usage = {**usage, "cost": cost}
    log_request(session_id, MODEL, full_usage, latency_ms, "tools" if req.use_tools else "")

    return ChatResponse(
        session_id=session_id,
        reply=reply,
        usage=full_usage,
        latency_ms=latency_ms,
    )


@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    """Server-Sent Events streaming endpoint (stream=True)."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="message must not be empty.")

    session_id = req.session_id or str(uuid.uuid4())
    if session_id not in chat_sessions:
        chat_sessions[session_id] = new_session(req.persona)
    session = chat_sessions[session_id]
    session["messages"].append({"role": "user", "content": req.message})
    system_instruction = build_system_instruction(session["persona"])

    # Same local tone check as /api/chat, adapted to the SSE shape: emit
    # the de-escalation reply as a single "delta" chunk (so the frontend's
    # existing streaming renderer needs no special case) then "done" —
    # the model is never called.
    tone = check_tone(req.message)
    if tone["flagged"]:
        def moderated_generator():
            turn_count = sum(1 for m in session["messages"] if m["role"] == "user")
            reply = moderated_response(tone["reasons"], turn_count)
            session["messages"].append({"role": "assistant", "content": reply})
            logger.info(json.dumps(log_moderation_event(session_id, tone["reasons"])))
            zero_usage = {"prompt_tokens": 0, "completion_tokens": 0, "cost": 0.0}
            yield f"data: {json.dumps({'delta': reply})}\n\n"
            yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'usage': zero_usage, 'latency_ms': 0, 'moderated': True})}\n\n"
        return StreamingResponse(moderated_generator(), media_type="text/event-stream")

    def event_generator():
        start = time.time()
        full_text = ""
        try:
            stream = client.models.generate_content_stream(
                model=MODEL,
                contents=build_contents(session["messages"]),
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=req.temperature,
                    top_p=req.top_p,
                    max_output_tokens=req.max_tokens,
                ),
            )
            usage = {"prompt_tokens": 0, "completion_tokens": 0}
            for chunk in stream:
                delta = chunk.text
                if delta:
                    full_text += delta
                    yield f"data: {json.dumps({'delta': delta})}\n\n"
                if chunk.usage_metadata:
                    usage = {
                        "prompt_tokens": chunk.usage_metadata.prompt_token_count or 0,
                        "completion_tokens": chunk.usage_metadata.candidates_token_count or 0,
                    }
            session["messages"].append({"role": "assistant", "content": full_text})
            latency_ms = int((time.time() - start) * 1000)
            cost = calculate_cost(MODEL, usage["prompt_tokens"], usage["completion_tokens"])
            session["usage"]["prompt_tokens"] += usage["prompt_tokens"]
            session["usage"]["completion_tokens"] += usage["completion_tokens"]
            session["usage"]["cost"] = round(session["usage"]["cost"] + cost, 6)
            log_request(session_id, MODEL, {**usage, "cost": cost}, latency_ms, "stream")
            yield f"data: {json.dumps({'done': True, 'session_id': session_id, 'usage': {**usage, 'cost': cost}, 'latency_ms': latency_ms, 'moderated': False})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/api/chat/regenerate")
def regenerate(req: RegenerateRequest):
    """
    Re-runs the last assistant turn WITHOUT appending a new user message.
    If the last message in the session is an assistant reply, it is
    dropped and replaced — this is what makes "regenerate" distinct from
    just resending the last question (which would duplicate the user
    turn and bloat the context on every retry).
    """
    session = chat_sessions.get(req.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    messages = session["messages"]
    if messages and messages[-1]["role"] == "assistant":
        messages.pop()

    if not messages or messages[-1]["role"] != "user":
        raise HTTPException(status_code=400, detail="Nothing to regenerate — no prior user message.")

    system_instruction = build_system_instruction(session["persona"])
    start = time.time()
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=build_contents(messages),
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.8,  # slightly higher so a regenerate actually varies
                max_output_tokens=600,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")

    reply = response.text or ""
    messages.append({"role": "assistant", "content": reply})

    latency_ms = int((time.time() - start) * 1000)
    um = response.usage_metadata
    usage = {
        "prompt_tokens": (um.prompt_token_count or 0) if um else 0,
        "completion_tokens": (um.candidates_token_count or 0) if um else 0,
    }
    cost = calculate_cost(MODEL, usage["prompt_tokens"], usage["completion_tokens"])
    session["usage"]["prompt_tokens"] += usage["prompt_tokens"]
    session["usage"]["completion_tokens"] += usage["completion_tokens"]
    session["usage"]["cost"] = round(session["usage"]["cost"] + cost, 6)

    full_usage = {**usage, "cost": cost}
    log_request(req.session_id, MODEL, full_usage, latency_ms, "regenerate")

    return ChatResponse(session_id=req.session_id, reply=reply, usage=full_usage, latency_ms=latency_ms)


@app.post("/api/prompts/structured-json")
def structured_json_prompt(req: ProductionPromptRequest):
    """
    Strict JSON-schema production prompt. Uses the API-level
    `response_json_schema` constraint AND validates the result locally
    against the `StudyPlan` pydantic model, retrying once with the
    validation error fed back to the model if it deviates.
    """
    template = PRODUCTION_PROMPTS["structured_json"]
    messages = [{"role": "user", "content": req.input}]

    last_error = None
    for attempt in range(2):  # one retry on schema deviation
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=build_contents(messages),
                config=types.GenerateContentConfig(
                    system_instruction=template["system"],
                    temperature=template["temperature"],
                    response_mime_type="application/json",
                    response_json_schema=STUDY_PLAN_SCHEMA,
                ),
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")

        raw = response.text or ""
        try:
            parsed = json.loads(raw)
            plan = StudyPlan(**parsed)  # local validation — the "handle deviation in code" step
            um = response.usage_metadata
            prompt_tokens = (um.prompt_token_count or 0) if um else 0
            completion_tokens = (um.candidates_token_count or 0) if um else 0
            return {
                "valid": True,
                "attempts": attempt + 1,
                "data": plan.model_dump(),
                "usage": {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "cost": calculate_cost(MODEL, prompt_tokens, completion_tokens),
                },
            }
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = str(e)
            messages.append({"role": "assistant", "content": raw})
            messages.append({
                "role": "user",
                "content": f"That output did not match the required schema ({last_error}). Return ONLY corrected JSON.",
            })

    # Both attempts failed validation — surface this clearly rather than
    # silently returning malformed data.
    raise HTTPException(
        status_code=500,
        detail=f"Model output did not conform to the JSON schema after 2 attempts: {last_error}",
    )


@app.post("/api/prompts/{prompt_type}")
def production_prompt(prompt_type: str, req: ProductionPromptRequest):
    """
    Generic runner for the remaining production prompt templates:
    text_parsing, code_generation, summarization.
    (structured_json has its own stricter endpoint above.)
    """
    if prompt_type not in PRODUCTION_PROMPTS or prompt_type == "structured_json":
        raise HTTPException(status_code=404, detail=f"Unknown prompt type '{prompt_type}'.")

    template = PRODUCTION_PROMPTS[prompt_type]
    start = time.time()
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=build_contents([{"role": "user", "content": req.input}]),
            config=types.GenerateContentConfig(
                system_instruction=template["system"],
                temperature=template["temperature"],
                max_output_tokens=800,
            ),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")

    latency_ms = int((time.time() - start) * 1000)
    um = response.usage_metadata
    usage = {
        "prompt_tokens": (um.prompt_token_count or 0) if um else 0,
        "completion_tokens": (um.candidates_token_count or 0) if um else 0,
    }
    cost = calculate_cost(MODEL, usage["prompt_tokens"], usage["completion_tokens"])
    log_request("n/a", MODEL, {**usage, "cost": cost}, latency_ms, f"prompt:{prompt_type}")

    return {
        "prompt_type": prompt_type,
        "output": response.text or "",
        "usage": {**usage, "cost": cost},
        "latency_ms": latency_ms,
    }


@app.post("/api/sessions/{session_id}/title")
def generate_title(session_id: str):
    """Auto-generate a short (3-5 word) title for the session via the LLM."""
    session = chat_sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found.")

    convo = [m for m in session["messages"] if m["role"] in ("user", "assistant")][:4]
    if not convo:
        return {"title": session["title"]}

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=build_contents(convo),
            config=types.GenerateContentConfig(
                system_instruction=TITLE_SYSTEM_PROMPT,
                temperature=0.3,
                max_output_tokens=20,
            ),
        )
        title = (response.text or "").strip().strip('"')
        session["title"] = title
        return {"title": title}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API error: {e}")


@app.post("/api/experiment/sampling")
def experiment_sampling(prompt: str, temperature_variants: str = "0.0,0.7,1.4"):
    """
    Generates 3 outputs for the same prompt at different temperature settings,
    for classroom demonstration of how sampling parameters change output.
    """
    temps = [float(t) for t in temperature_variants.split(",")]
    results = []
    for t in temps:
        response = client.models.generate_content(
            model=MODEL,
            contents=build_contents([{"role": "user", "content": prompt}]),
            config=types.GenerateContentConfig(
                temperature=t,
                max_output_tokens=150,
            ),
        )
        results.append({
            "temperature": t,
            "output": response.text or "",
        })
    return {"prompt": prompt, "results": results}


@app.get("/api/personas")
def get_personas():
    return {name: prompt for name, prompt in PERSONAS.items()}
