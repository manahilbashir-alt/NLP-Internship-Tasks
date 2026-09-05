"""
DAY 23 - CONTENT SAFETY / PROFANITY FILTER
============================================================
Requirement covered: "bad words sab kuch achi trah deal kro"
(handle bad/abusive language properly, everywhere).

This module is applied on every text entry point into the
system:

    1. Typed questions          -> /api/rag/chat
    2. Typed questions (stream) -> /api/rag/chat/stream
    3. Typed questions (voice)  -> /api/rag/chat/voice
    4. Transcribed speech       -> /api/transcribe (Whisper output)

Design:
    - MILD profanity is *censored* (letters replaced with "*"),
      the cleaned text is still sent to the RAG pipeline, so a
      user who curses out of frustration still gets an answer.
    - SEVERE / hateful / harassing language causes the request
      to be *rejected* before it ever reaches Gemini or XTTS,
      with a short, polite message returned instead.

This is a lightweight, dependency-free word-list filter (no
extra model download, so it works instantly on any machine).
It is intentionally conservative: it only catches whole words
(word-boundary matching), not substrings, to avoid false
positives like "assist" or "classic".
"""

import re

# ------------------------------------------------------------
# Word lists. Kept short and generic on purpose - this is a
# guardrail for a document-QA assistant, not a full trust &
# safety system. Extend these sets as needed for your deployment.
# ------------------------------------------------------------

MILD_PROFANITY = {
    "damn", "hell", "crap", "ass", "piss", "bastard", "bloody",
    "shit", "fuck", "fucking", "fucked", "bullshit", "dumbass",
}

SEVERE_TERMS = {
    # slurs / hateful or harassing language and explicit threats
    # are rejected outright rather than censored.
    "kill yourself", "kys", "i will kill you", "i'll kill you",
    "terrorist attack", "bomb the", "make a bomb",
}

_MASK = lambda w: w[0] + "*" * (len(w) - 1)


def _wrap(word: str) -> re.Pattern:
    return re.compile(rf"\b{re.escape(word)}\b", flags=re.IGNORECASE)


_MILD_PATTERNS = [(w, _wrap(w)) for w in MILD_PROFANITY]


def moderate_text(text: str) -> dict:
    """
    Runs a piece of user-supplied text (typed OR transcribed)
    through the filter.

    Returns:
        {
            "blocked": bool,        # True -> reject the request entirely
            "cleaned_text": str,    # profanity-masked version, safe to
                                     # forward to the RAG pipeline / TTS
            "flagged": [str, ...],  # words/phrases that were caught
            "reason": str | None,   # human-readable reason if blocked
        }
    """
    if not text:
        return {"blocked": False, "cleaned_text": text, "flagged": [], "reason": None}

    lowered = text.lower()

    for phrase in SEVERE_TERMS:
        if phrase in lowered:
            return {
                "blocked": True,
                "cleaned_text": text,
                "flagged": [phrase],
                "reason": (
                    "That message contains language I can't act on "
                    "(threats or hateful content). Please rephrase your "
                    "question and I'll be glad to help."
                ),
            }

    cleaned = text
    flagged = []
    for word, pattern in _MILD_PATTERNS:
        if pattern.search(cleaned):
            flagged.append(word)
            cleaned = pattern.sub(lambda m: _MASK(m.group(0)), cleaned)

    return {"blocked": False, "cleaned_text": cleaned, "flagged": flagged, "reason": None}


content_filter = {"moderate_text": moderate_text}
