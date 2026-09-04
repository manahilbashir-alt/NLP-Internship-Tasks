import sys
from pathlib import Path

DAY18_PATH = Path.home() / "Documents/AI-Engineering/day18_RAG_Pipeline"
sys.path.insert(0, str(DAY18_PATH))

from rag.retriever import Retriever
from backend.retrieval.hybrid_search import hybrid_search
from reranker import rerank
from parent_expander import expand_to_parent


def hierarchical_search(query, vector_retriever, top_k=3, window=2):
    # Step 1: find small precise chunks (same as before)
    candidates = hybrid_search(query, vector_retriever, candidate_k=20, top_k=20)
    top_chunks = rerank(query, candidates, top_k=top_k)

    # Step 2: expand each one into a bigger passage
    expanded_results = []
    for chunk in top_chunks:
        expanded = expand_to_parent(chunk["chunk_id"], window=window)
        expanded_results.append({
            "original_chunk_id": chunk["chunk_id"],
            "expanded_text": expanded["combined_text"],
            "chunks_included": expanded["chunk_ids"],
        })
    return expanded_results


if __name__ == "__main__":
    retriever = Retriever()
    query = "explain support vector machines"

    results = hierarchical_search(query, retriever, top_k=3, window=2)

    for rank, r in enumerate(results, start=1):
        print(f"#{rank}  matched chunk: {r['original_chunk_id']}")
        print(f"     expanded to: {r['chunks_included']}")
        print(f"     text length: {len(r['expanded_text'])} characters\n")