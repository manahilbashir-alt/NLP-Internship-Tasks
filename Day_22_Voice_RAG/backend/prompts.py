"""
Centralized LLM prompt templates.

Every prompt the backend sends to Gemini lives here instead of being an
inline f-string inside chat/eval logic. Two reasons:

1. Review/versioning — prompts are the part of a RAG system most likely to
   need tweaking after looking at real answers; keeping them in one file
   means you don't have to hunt through business logic to change wording.
2. Reuse — `chat/conversational_chain.py` (live chat) and
   `evaluation/run_generation_eval.py` (offline eval) both need an
   "answer using only this context" prompt. They now share the exact same
   template via `build_answer_prompt`, so eval results actually reflect
   what the live endpoint would produce.

Each prompt below is a plain `str.format`-style template plus a small
`build_*` helper that fills it in. The helpers are what the rest of the
codebase imports/calls — treat the raw template strings as internal.
"""

# ---------------------------------------------------------------------------
# Question rewriting — turns a follow-up ("what about its disadvantages?")
# into a standalone question using the conversation so far.
# ---------------------------------------------------------------------------
QUESTION_REWRITE_PROMPT = """Given this conversation so far:
{history_text}

Rewrite this follow-up question so it can be understood on its own, without \
needing the conversation above. Only output the rewritten question, nothing \
else.

Follow-up question: {question}
Standalone question:"""


def build_question_rewrite_prompt(question: str, history_text: str) -> str:
    """Prompt used to rewrite a follow-up question into a standalone one.

    `history_text` should already be formatted as alternating
    "Role: message" lines (see `conversational_chain.py`'s history join).
    """
    return QUESTION_REWRITE_PROMPT.format(question=question, history_text=history_text)


# ---------------------------------------------------------------------------
# Answering — grounds the answer strictly in retrieved context, with an
# explicit instruction to say "I don't know" rather than hallucinate.
# ---------------------------------------------------------------------------
ANSWER_PROMPT = """Answer the question using ONLY the context below. If the \
answer isn't in the context, say you don't know.

Context:
{context}

Conversation so far:
{history_text}

Question: {question}
Answer:"""

# Same instruction, without a conversation-history section — used by the
# offline evaluation script, which asks each question fresh (no chat turns).
ANSWER_PROMPT_NO_HISTORY = """Answer the question using ONLY the context \
below. If the answer isn't in the context, say you don't know.

Context:
{context}

Question: {question}
Answer:"""


def build_answer_prompt(question: str, context: str, history_text: str = "") -> str:
    """Prompt used to generate the final answer from retrieved context.

    Pass `history_text` (alternating "Role: message" lines) for the live
    chat flow; omit it (default "") for one-off / evaluation questions.
    """
    if history_text:
        return ANSWER_PROMPT.format(question=question, context=context, history_text=history_text)
    return ANSWER_PROMPT_NO_HISTORY.format(question=question, context=context)
