"""
moderation.py
==============
Local (no API call) tone check that runs on every incoming user message
*before* it reaches the model. Two independent layers of defense, on
purpose:

  1. This module — a fast, free, local heuristic that catches profanity
     and shouting-at-the-bot before a single token is sent to the API.
     Zero latency, zero cost, and it means an abusive message never even
     becomes part of the model's context.
  2. `PERSONA_GUARDRAIL_SUFFIX` in prompts.py — a model-level instruction
     that keeps every persona calm and non-mirroring even for messages
     that are harsh but don't trip the local filter (sarcasm, a curse
     word this list doesn't know, frustration without any single "bad"
     word, etc).

Layer 1 catches the obvious/cheap cases; layer 2 is the fallback for
everything subtler. Neither one is meant to be a bulletproof classifier —
this is a classroom-scale project, not a production trust & safety
pipeline — but together they mean the tutor never has to see, or respond
in kind to, a hostile message.
"""

import re
from datetime import datetime

# ---------------------------------------------------------------------------
# Signal 1: profanity / abusive language
# ---------------------------------------------------------------------------
# A small, intentionally generic word list (not exhaustive — this is a
# heuristic, not a content-moderation product). Matched on whole words
# only, case-insensitively, so it doesn't false-positive on substrings
# inside legitimate words.

_ABUSIVE_WORDS = [
    "idiot", "stupid", "dumb", "moron", "useless", "trash", "garbage",
    "shut up", "hate you", "worthless", "pathetic", "loser",
    "fuck", "shit", "bitch", "asshole", "bastard", "damn you",
    "screw you", "piece of crap", "crap",
]

_WORD_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in _ABUSIVE_WORDS) + r")\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Signal 2: shouting / aggressive punctuation (harsh tone without profanity)
# ---------------------------------------------------------------------------

def _is_shouting(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    if len(letters) < 6:
        return False
    upper_ratio = sum(1 for c in letters if c.isupper()) / len(letters)
    return upper_ratio > 0.7


def _has_aggressive_punctuation(text: str) -> bool:
    return bool(re.search(r"[!?]{3,}", text))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def check_tone(text: str) -> dict:
    """
    Runs the local heuristic checks on a user message.
    Returns: {"flagged": bool, "reasons": list[str]}
    Never raises — worst case it under-flags, it doesn't crash the request.
    """
    reasons = []
    match = _WORD_PATTERN.search(text or "")
    if match:
        reasons.append("abusive_language")
    if _is_shouting(text or ""):
        reasons.append("shouting")
    if _has_aggressive_punctuation(text or ""):
        reasons.append("aggressive_punctuation")

    return {"flagged": len(reasons) > 0, "reasons": reasons}


_DEESCALATION_REPLIES = [
    "I want to help, but I'll need us to keep things respectful. "
    "Take a breath, rephrase that, and let's get back to your question.",
    "I hear that you're frustrated — that's completely fair when you're "
    "stuck on something. I just can't respond to insults or shouting. "
    "Try asking again in your own words and I'm glad to dig in with you.",
    "Let's reset for a second. I'm here to help you learn, not to be "
    "yelled at or insulted, so I won't respond to that message as written. "
    "What are you actually trying to figure out? Ask me that.",
]


def moderated_response(reasons: list[str], turn_count: int = 0) -> str:
    """
    Picks a de-escalation reply. Deterministic (based on turn_count) rather
    than random, so behavior is reproducible in tests and demos.
    """
    return _DEESCALATION_REPLIES[turn_count % len(_DEESCALATION_REPLIES)]


def log_moderation_event(session_id: str, reasons: list[str]) -> dict:
    """Structured event for the same logger main.py already uses, so
    moderation shows up in the same log stream as everything else."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "event": "moderation_flag",
        "reasons": reasons,
    }
