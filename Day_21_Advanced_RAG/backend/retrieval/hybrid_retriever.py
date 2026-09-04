from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from pydantic import PrivateAttr

from chat.langchain_retriever import get_langchain_retriever
from retrieval.bm25_retriever import BM25Retriever


def rrf_fuse(bm25_results, vector_results, k=60, top_k=5):
    scores, content_map = {}, {}
    for rank, r in enumerate(bm25_results):
        cid = r["chunk_id"]
        scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank + 1)
        content_map[cid] = r["content"]
    for rank, r in enumerate(vector_results):
        cid = r["chunk_id"]
        scores[cid] = scores.get(cid, 0) + 1.0 / (k + rank + 1)
        content_map[cid] = r["content"]
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]
    return [{"chunk_id": cid, "content": content_map[cid], "rrf_score": s} for cid, s in ranked]


class HybridRetriever(BaseRetriever):
    k: int = 5
    _vector_retriever: object = PrivateAttr()
    _bm25: object = PrivateAttr()

    def __init__(self, k=5, **kwargs):
        super().__init__(k=k, **kwargs)
        self._vector_retriever = get_langchain_retriever(k=k)
        self._bm25 = BM25Retriever()

    def reload(self):
        self._vector_retriever.reload()
        self._bm25.reload()

    def _get_relevant_documents(self, query: str) -> list[Document]:
        bm25_results = self._bm25.search(query, top_k=20)
        vector_results = self._vector_retriever.search_raw(query, k=20)
        fused = rrf_fuse(bm25_results, vector_results, top_k=self.k)

        by_id = {m["chunk_id"]: m for m in self._vector_retriever._row_metadata}
        docs = []
        for r in fused:
            meta = by_id.get(r["chunk_id"], {})
            docs.append(Document(
                page_content=r["content"],
                metadata={
                    "chunk_id": r["chunk_id"],
                    "source_file": meta.get("source_file"),
                    "page_no": meta.get("page_no"),
                    "section": meta.get("section"),
                    "rrf_score": r["rrf_score"],
                },
            ))
        return docs


def get_hybrid_retriever(k=5):
    return HybridRetriever(k=k)