"""
================================================================================
 DAY 21 — GENERATION EVAL: real Gemini answers across all 4 methods
================================================================================
WHAT THIS DOES:
  Unlike run_evaluation.py (retrieval-only, no LLM calls), this script
  actually generates a real answer with Gemini for each (method, question)
  pair — giving genuine accuracy, source precision, and hallucination data,
  not just a retrieval proxy.

  Gemini's free tier caps at ~20 requests/day, so this only runs on a small
  SAMPLE of your 20 questions (see SAMPLE_SIZE below), not all 20 — running
  all 20 x 4 methods = 80 calls would blow the daily quota instantly.
  This is disclosed as a real limitation in the README, not hidden.

  SAMPLE_SIZE x 4 methods = total Gemini calls used by this run.
  SAMPLE_SIZE=3 -> 12 calls (safe). SAMPLE_SIZE=5 -> 20 calls (uses full quota).

METRICS PER (method, question):
  - accuracy_proxy      : keyword overlap between the GENERATED ANSWER and
                           the expected_fact (rough correctness signal —
                           not human judgment, disclosed as a heuristic)
  - source_precision_hit : did the top cited page match expected_page_hint?
                           (only scored for questions that have a hint)
  - hallucination_flag   : True if the answer's content has LOW overlap with
                           the actually-retrieved context AND the answer
                           isn't an "I don't know" — i.e. it asserted things
                           not grounded in what was retrieved. This is a
                           heuristic, not a semantic entailment check.

HOW TO RUN (from backend/, with venv18 active):
  python evaluation/run_generation_eval.py
================================================================================
"""

import sys
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from prompts import build_answer_prompt

BACKEND_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_PATH = BACKEND_ROOT / "evaluation" / "questions.json"
RESULTS_PATH = BACKEND_ROOT / "evaluation" / "generation_results.json"

SAMPLE_SIZE = 3   # <-- adjust based on remaining Gemini quota today
K = 3

UNCERTAIN_PHRASES = ["i don't know", "i do not know", "not provided in the text", "not fully listed"]


def is_uncertain(text):
    t = (text or "").lower()
    return any(p in t for p in UNCERTAIN_PHRASES)


def significant_words(text):
    words = re.findall(r"[a-zA-Z]{4,}", text.lower())
    stop = {"with", "that", "this", "from", "into", "used", "were", "have",
            "based", "using", "such", "each", "when", "than", "what", "provided", "context"}
    return [w for w in words if w not in stop]


def coverage(a_text, b_text):
    words = set(significant_words(a_text))
    if not words:
        return 0.0
    combined = b_text.lower()
    hits = sum(1 for w in words if w in combined)
    return round(hits / len(words), 3)


def page_hit(expected_page, retrieved_pages):
    if expected_page is None:
        return None
    return any(abs((p or -999) - expected_page) <= 1 for p in retrieved_pages)


def main():
    questions = json.loads(QUESTIONS_PATH.read_text(encoding="utf-8"))[:SAMPLE_SIZE]
    print(f"[gen-eval] Running {len(questions)} questions x 4 methods = {len(questions)*4} Gemini calls\n")

    from langchain_google_genai import ChatGoogleGenerativeAI
    from chat.langchain_retriever import get_langchain_retriever
    from retrieval.bm25_retriever import BM25Retriever
    from retrieval.hybrid_retriever import get_hybrid_retriever
    from retrieval.hierarchical_retriever import get_hierarchical_retriever

    llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest")

    print("[gen-eval] Loading retrievers...")
    simple = get_langchain_retriever(k=K)
    bm25 = BM25Retriever()
    hybrid = get_hybrid_retriever(k=K)
    hierarchical = get_hierarchical_retriever(k=K, window=2)

    def get_text(response):
        content = response.content
        if isinstance(content, list):
            content = "".join(p if isinstance(p, str) else p.get("text", "") for p in content)
        return content.strip()

    def context_and_pages_simple_like(retriever, query):
        docs = retriever.invoke(query)
        pages = [d.metadata.get("page_no") for d in docs]
        texts = [d.page_content for d in docs]
        return "\n\n".join(texts), pages

    def context_and_pages_bm25(query):
        results = bm25.search(query, top_k=K)
        by_id = {c["chunk_id"]: c for c in bm25.chunks}
        pages, texts = [], []
        for r in results:
            meta = by_id.get(r["chunk_id"], {})
            pages.append(meta.get("page_no"))
            texts.append(r["content"])
        return "\n\n".join(texts), pages

    methods = {
        "Simple": lambda q: context_and_pages_simple_like(simple, q),
        "BM25": lambda q: context_and_pages_bm25(q),
        "Hybrid": lambda q: context_and_pages_simple_like(hybrid, q),
        "Hierarchical": lambda q: context_and_pages_simple_like(hierarchical, q),
    }

    all_results = {name: [] for name in methods}
    call_count = 0

    for q in questions:
        print(f"\n[gen-eval] Q{q['id']}: {q['question']}")
        for method_name, get_ctx in methods.items():
            context, pages = get_ctx(q["question"])
            prompt = build_answer_prompt(q["question"], context)
            response = llm.invoke(prompt)
            call_count += 1
            answer = get_text(response)
            uncertain = is_uncertain(answer)

            accuracy_proxy = coverage(q["expected_fact"], answer)
            grounding = coverage(answer, context)  # how much of the ANSWER is backed by context
            hallucination_flag = (not uncertain) and grounding < 0.35
            precision_hit = page_hit(q["expected_page_hint"], pages)

            print(f"  [{method_name}] uncertain={uncertain} accuracy_proxy={accuracy_proxy} "
                  f"grounding={grounding} hallucination_flag={hallucination_flag}")

            all_results[method_name].append({
                "id": q["id"],
                "question": q["question"],
                "answer": answer,
                "uncertain": uncertain,
                "accuracy_proxy": accuracy_proxy,
                "grounding_score": grounding,
                "hallucination_flag": hallucination_flag,
                "source_precision_hit": precision_hit,
                "retrieved_pages": pages,
            })

    print(f"\n[gen-eval] Total Gemini calls used: {call_count}")

    summary = {}
    for method_name, rows in all_results.items():
        hinted = [r for r in rows if r["source_precision_hit"] is not None]
        summary[method_name] = {
            "avg_accuracy_proxy": round(sum(r["accuracy_proxy"] for r in rows) / len(rows), 3),
            "hallucination_rate": round(sum(1 for r in rows if r["hallucination_flag"]) / len(rows), 3),
            "source_precision": (
                round(sum(1 for r in hinted if r["source_precision_hit"]) / len(hinted), 3)
                if hinted else None
            ),
            "source_precision_n": len(hinted),
        }

    print("\n" + "=" * 80)
    print(f"{'Method':<14}{'Accuracy proxy':<18}{'Hallucination rate':<20}{'Source precision':<18}")
    print("=" * 80)
    for method_name, s in summary.items():
        sp = f"{s['source_precision']} (n={s['source_precision_n']})" if s["source_precision"] is not None else "n/a"
        print(f"{method_name:<14}{s['avg_accuracy_proxy']:<18}{s['hallucination_rate']:<20}{sp:<18}")

    RESULTS_PATH.write_text(
        json.dumps({"per_question": all_results, "summary": summary, "sample_size": SAMPLE_SIZE}, indent=2),
        encoding="utf-8",
    )
    print(f"\n[gen-eval] Full results saved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()