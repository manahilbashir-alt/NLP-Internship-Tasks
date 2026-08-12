"""
Stateless `generate_content` vs. stateful `client.chats` session — a
side-by-side demo of the two main ways to call the Gemini API.

Run: python api_comparison_demo.py
(requires GEMINI_API_KEY in the environment)

STRUCTURAL DIFFERENCES (documented from hands-on use):

1. Input shape
   - generate_content: `contents=[...]` — a list of `Content` objects
     (or a plain string for a single-turn prompt). You resend the
     *entire* conversation history yourself on every call, exactly like
     this project's `build_contents()` helper does for `/api/chat`.
   - client.chats.create(...): returns a `Chat` object that keeps the
     history internally. You call `chat.send_message("...")` per turn
     and never have to replay prior turns yourself.

2. Output shape
   - generate_content: `response.text` is a convenience property that
     flattens all text parts of `response.candidates[0].content`.
     Function calls are exposed via `response.function_calls`.
   - chats: `chat.send_message(...)` returns the same
     `GenerateContentResponse` type, so `.text` / `.function_calls`
     work identically — the only difference is the SDK manages history
     for you between calls.

3. Statefulness
   - generate_content is fully stateless; the caller owns history
     (this is what `main.py` uses, since our FastAPI layer already owns
     an explicit per-session message list that needs to be inspectable,
     editable, and JSON-serializable for the sidebar/session endpoints).
   - client.chats is stateful client-side: the `Chat` object accumulates
     `history` for you, which is convenient for quick scripts/notebooks
     but less useful once you need to persist, branch, or inspect state
     server-side across requests, the way a web backend does.

4. Built-in tools
   - Both entry points accept the same `config=types.GenerateContentConfig(
     tools=[...])`, including custom function declarations (used by
     `run_tool_loop()` in main.py) as well as Google-hosted tools like
     `google_search` or `code_execution`.

5. Streaming
   - generate_content_stream(...) yields `GenerateContentResponse` chunks
     with incremental `.text` deltas — used by `/api/chat/stream`.
   - chat.send_message_stream(...) does the same thing but also updates
     the chat's internal history once the stream completes.

This project's backend (main.py) uses `generate_content` /
`generate_content_stream` throughout, because the FastAPI session store
already owns the full message array explicitly (for the sidebar, usage
tracking, and title generation) — a stateful `Chat` object would just be
a second copy of the same state. `client.chats` becomes attractive for
quick scripts or notebooks where you don't want to manage a message list
yourself.
"""

import os
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
MODEL = "gemini-3.1-flash-lite"
SYSTEM = "You are a concise study tutor."
PROMPT = "In one sentence, what is spaced repetition?"


def generate_content_demo():
    response = client.models.generate_content(
        model=MODEL,
        contents=[types.Content(role="user", parts=[types.Part.from_text(text=PROMPT)])],
        config=types.GenerateContentConfig(system_instruction=SYSTEM),
    )
    um = response.usage_metadata
    return {
        "text": response.text,
        "usage": {
            "prompt_tokens": um.prompt_token_count if um else None,
            "completion_tokens": um.candidates_token_count if um else None,
        },
    }


def chats_session_demo():
    chat = client.chats.create(
        model=MODEL,
        config=types.GenerateContentConfig(system_instruction=SYSTEM),
    )
    response = chat.send_message(PROMPT)
    um = response.usage_metadata
    return {
        "text": response.text,
        "usage": {
            "prompt_tokens": um.prompt_token_count if um else None,
            "completion_tokens": um.candidates_token_count if um else None,
        },
        "history_length": len(chat.get_history()),  # managed by the SDK
    }


if __name__ == "__main__":
    if not os.environ.get("GEMINI_API_KEY"):
        raise SystemExit("Set GEMINI_API_KEY first.")

    print("=== generate_content (stateless) ===")
    print(generate_content_demo())

    print("\n=== client.chats (stateful session) ===")
    print(chats_session_demo())
