from sentence_transformers import CrossEncoder

CROSS_ENCODER_MODEL = "cross-encoder/ms-marco-MiniLM-L-12-v2"

_model = None  # loaded once, reused across calls

def get_reranker():
    global _model
    if _model is None:
        print(f"[reranker] Loading {CROSS_ENCODER_MODEL}...")
        _model = CrossEncoder(CROSS_ENCODER_MODEL)
    return _model


def rerank(query: str, candidates: list, top_k: int = 5) -> list:
    """
    candidates: list of dicts with at least "chunk_id" and "content"
                (this is what hybrid_search() already returns).
    Returns the same dicts, re-sorted by cross-encoder relevance,
    with a new "rerank_score" field added.
    """
    if not candidates:
        return []

    model = get_reranker()

    # Cross-encoder needs (query, chunk_text) pairs
    pairs = [(query, c["content"]) for c in candidates]
    scores = model.predict(pairs)

    for c, score in zip(candidates, scores):
        c["rerank_score"] = round(float(score), 4)

    reranked = sorted(candidates, key=lambda c: c["rerank_score"], reverse=True)
    return reranked[:top_k]


if __name__ == "__main__":
    import sys
    from pathlib import Path

    DAY18_PATH = Path.home() / "Documents/AI-Engineering/day18_RAG_Pipeline"
    sys.path.insert(0, str(DAY18_PATH))

    from rag.retriever import Retriever
    from backend.retrieval.hybrid_search import hybrid_search

    retriever = Retriever()
    query = "explain support vector machines"

    # Get a bigger candidate pool from hybrid search (top 20, not top 5)
    candidates = hybrid_search(query, retriever, candidate_k=20, top_k=20)
    print(f"Hybrid gave {len(candidates)} candidates\n")

    reranked = rerank(query, candidates, top_k=5)
    print(f"After cross-encoder re-ranking (top 5):\n")
    for rank, r in enumerate(reranked, start=1):
        preview = r["content"][:100].replace("\n", " ")
        print(f"#{rank}  rerank_score={r['rerank_score']}  {r['chunk_id']}")
        print(f"     \"{preview}...\"\n")