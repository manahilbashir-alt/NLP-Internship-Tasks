"""
retrieval.py

Hybrid retrieval: dense (vector store) + sparse (BM25), merged with
reciprocal rank fusion. Dense catches paraphrases and semantic
neighbors; BM25 catches exact terms, IDs, and jargon dense embeddings
tend to blur together. Fusing beats picking one or the other on most
corpora we've thrown at this in practice.
"""

from rank_bm25 import BM25Okapi
from src.chunking import Chunk
from src.vector_store import VectorStore
class HybridRetriever:
    def __init__(self, store: VectorStore, embedder, chunks: list[Chunk]):
        self.store = store
        self.embedder = embedder
        self.chunks = {c.chunk_id: c for c in chunks}
        tokenized = [c.text.lower().split() for c in chunks]
        self.bm25 = BM25Okapi(tokenized) if tokenized else None
        self.bm25_ids = [c.chunk_id for c in chunks]

    def _bm25_search(self, query: str, top_k: int) -> list[str]:
        if not self.bm25:
            return []
        scores = self.bm25.get_scores(query.lower().split())
        ranked = sorted(zip(self.bm25_ids, scores), key=lambda x: x[1], reverse=True)
        return [cid for cid, score in ranked[:top_k] if score > 0]

    def _dense_search(self, query: str, top_k: int) -> list[str]:
        q_emb = self.embedder.embed([query])[0]
        hits = self.store.query_similar(q_emb, top_k=top_k)
        return [h["chunk_id"] for h in hits]

    def retrieve(self, query: str, top_k: int = 5, candidate_k: int = 20, rrf_k: int = 60):
        """
        Pull candidate_k from each method, fuse rankings with reciprocal
        rank fusion (score = sum of 1/(rrf_k + rank) across methods), and
        return the top_k fused results. rrf_k=60 is the usual default
        from the original RRF paper - it dampens how much rank 1 vs
        rank 2 matters, works fine untuned for most cases.
        """
        dense_ids = self._dense_search(query, candidate_k)
        sparse_ids = self._bm25_search(query, candidate_k)

        fused_scores: dict[str, float] = {}
        for rank, cid in enumerate(dense_ids):
            fused_scores[cid] = fused_scores.get(cid, 0) + 1 / (rrf_k + rank + 1)
        for rank, cid in enumerate(sparse_ids):
            fused_scores[cid] = fused_scores.get(cid, 0) + 1 / (rrf_k + rank + 1)

        ranked = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for cid, score in ranked:
            chunk = self.chunks.get(cid)
            if chunk:
                results.append({"chunk_id": cid, "text": chunk.text, "source": chunk.source,
                                 "metadata": chunk.metadata, "fused_score": score})
        return results
