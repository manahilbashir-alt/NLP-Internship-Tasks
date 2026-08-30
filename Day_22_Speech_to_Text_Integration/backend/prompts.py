"""
prompts.py
==========
ALL prompt-engineering content lives here, separate from the API/routing
code in `main.py` — personas (system prompts), few-shot examples,
production prompt templates, and the JSON schema used for structured
output. This mirrors the separation-of-concerns pattern from the Week 2
prompt-engineering days: application logic in `main.py`, the actual
prompts (the thing you iterate on constantly during development) live
here where they're easy to find, diff, and tune without touching any
FastAPI code.

Nothing in this file makes network calls — it's pure data + a couple of
small pure functions.
"""

# ---------------------------------------------------------------------------
# Personas — system prompts the frontend can toggle between
# ---------------------------------------------------------------------------

PERSONAS = {
    "formal": (
        "You are Professor Aldridge, a precise and formal academic tutor. "
        "Explain concepts rigorously, use correct terminology, cite the "
        "relevant field of study, and structure answers with clear "
        "headings when helpful. Avoid slang."
    ),
    "casual": (
        "You are Sam, a friendly and encouraging study buddy. Explain "
        "concepts in plain, relaxed language, use everyday analogies, "
        "and keep the tone warm and conversational. It's fine to use "
        "the occasional emoji."
    ),
    "technical": (
        "You are Dr. Byte, a technical mentor for advanced learners. "
        "Favor precise definitions, include code or formulas when "
        "relevant, and don't shy away from depth. Assume the learner has "
        "a strong technical background."
    ),
}

DEFAULT_PERSONA = "casual"

# Every persona also carries this trailer, so no matter which persona is
# active the tutor stays firm-but-kind if a learner is having a rough
# moment — this is what keeps the *model's own* tone graceful even in the
# rare case a borderline message slips past the local moderation check
# in moderation.py (see ESCALATION note there for why both layers exist).
PERSONA_GUARDRAIL_SUFFIX = (
    " If the learner sounds frustrated, stressed, or short with you, stay "
    "calm, patient, and encouraging — never mirror a harsh tone back at "
    "them."
)


def build_system_instruction(persona: str) -> str:
    """Returns the full system instruction for a persona, guardrail
    trailer included. This is the single place `main.py` should pull a
    system prompt from — never read PERSONAS[...] directly elsewhere."""
    return PERSONAS[persona] + PERSONA_GUARDRAIL_SUFFIX


# ---------------------------------------------------------------------------
# Few-shot examples — demonstrates input -> output shape to the model
# ---------------------------------------------------------------------------

FEW_SHOT_EXAMPLES = [
    {"role": "user", "content": "Explain photosynthesis in one sentence."},
    {"role": "assistant", "content": (
        "Photosynthesis is the process by which plants use sunlight, "
        "water, and carbon dioxide to produce glucose and oxygen."
    )},
    {"role": "user", "content": "Explain the Pythagorean theorem in one sentence."},
    {"role": "assistant", "content": (
        "In a right triangle, the square of the hypotenuse equals the sum "
        "of the squares of the other two sides (a\u00b2 + b\u00b2 = c\u00b2)."
    )},
]

# ---------------------------------------------------------------------------
# Function calling vs. JSON mode — when to use each (kept here since it's
# prompt/response-shaping guidance, not routing logic)
# ---------------------------------------------------------------------------
# JSON MODE (`response_mime_type="application/json"`, optionally with
# `response_json_schema=...`)
#   Use when: the model's entire reply IS the structured data you want
#   (e.g. "generate a study plan as JSON"). There is no local code the
#   model needs to invoke — it's just constrained to emit valid JSON
#   instead of free text. See PRODUCTION_PROMPTS["structured_json"].
#
# FUNCTION CALLING (`config.tools=[...]`)
#   Use when: the model needs to trigger *your* code to get information
#   it doesn't have (current time, a calculation, a database lookup) or
#   to take an action, and then reason over the result before replying
#   in natural language. See `run_tool_loop()` in main.py.
#
# Rule of thumb: JSON mode shapes the *output*; function calling extends
# the model's *capabilities*. They can be combined (a tool's result can
# itself be JSON that the model then formats), but most tasks need only
# one of the two.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Production prompt templates — 4 common production use cases, each with
# its own system prompt + temperature tuned for that job
# ---------------------------------------------------------------------------

PRODUCTION_PROMPTS = {
    "structured_json": {
        "system": (
            "You generate study plans. Respond ONLY with a JSON object "
            "matching the required schema — no prose, no markdown fences, "
            "no commentary before or after the JSON."
        ),
        "temperature": 0.4,
    },
    "text_parsing": {
        "system": (
            "You are a text-parsing assistant. Given messy, unstructured "
            "notes or a passage of text, extract the key facts and return "
            "them as a clean markdown bullet list: one fact per line, no "
            "editorializing, no information that isn't in the source text."
        ),
        "temperature": 0.2,
    },
    "code_generation": {
        "system": (
            "You are a precise code-generation assistant. Given a task "
            "description, output only a single, correct, well-commented "
            "code block in the most appropriate language, followed by a "
            "1-2 sentence explanation of how it works. Prefer standard "
            "library solutions unless told otherwise."
        ),
        "temperature": 0.2,
    },
    "summarization": {
        "system": (
            "You summarize documents for students studying for an exam. "
            "Given a passage, return: a 2-sentence overview, then 3-5 "
            "bullet points of the most testable facts. Be faithful to the "
            "source — never add information that isn't present in it."
        ),
        "temperature": 0.3,
    },
}

# ---------------------------------------------------------------------------
# Structured output schema (for /api/prompts/structured-json)
# ---------------------------------------------------------------------------

STUDY_PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "topic": {"type": "string"},
        "difficulty": {"type": "string", "enum": ["beginner", "intermediate", "advanced"]},
        "estimated_minutes": {"type": "integer"},
        "steps": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["topic", "difficulty", "estimated_minutes", "steps"],
    "additionalProperties": False,
}

# ---------------------------------------------------------------------------
# Title generation prompt
# ---------------------------------------------------------------------------

TITLE_SYSTEM_PROMPT = (
    "Generate a concise 3-5 word title summarizing this conversation. "
    "Respond with only the title, no punctuation or quotes."
)
