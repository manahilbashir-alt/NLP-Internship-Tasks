from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from pydantic import PrivateAttr

from chat.langchain_retriever import get_langchain_retriever
from retrieval.bm25_retriever import BM25Retriever
from retrieval.hybrid_retriever import rrf_fuse
from retrieval.reranker import rerank
from retrieval.parent_expander import ParentExpander


class HierarchicalRetriever(BaseRetriever):
    k: int = 3
    window: int = 2
    _vector_retriever: object = PrivateAttr()
    _bm25: object = PrivateAttr()
    _expander: object = PrivateAttr()

    def __init__(self, k=3, window=2, **kwargs):
        super().__init__(k=k, window=window, **kwargs)
        self._vector_retriever = get_langchain_retriever(k=20)
        self._bm25 = BM25Retriever()
        self._expander = ParentExpander()

    def reload(self):
        self._vector_retriever.reload()
        self._bm25.reload()
        self._expander.reload()

    def _get_relevant_documents(self, query: str) -> list[Document]:
        # 1. Hybrid: wide candidate pool
        bm25_results = self._bm25.search(query, top_k=20)
        vector_results = self._vector_retriever.search_raw(query, k=20)
        fused = rrf_fuse(bm25_results, vector_results, top_k=20)

        # 2. Rerank: narrow to the best few, on the SMALL chunks
        reranked = rerank(query, fused, top_k=self.k)

        # 3. Expand: only the survivors get widened with neighbors
        by_id = {m["chunk_id"]: m for m in self._vector_retriever._row_metadata}
        docs = []
        for r in reranked:
            expanded = self._expander.expand(r["chunk_id"], window=self.window)
            meta = by_id.get(r["chunk_id"], {})
            docs.append(Document(
                page_content=expanded["combined_text"],
                metadata={
                    "chunk_id": r["chunk_id"],
                    "expanded_chunk_ids": expanded["chunk_ids"],
                    "source_file": meta.get("source_file"),
                    "page_no": meta.get("page_no"),
                    "section": meta.get("section"),
                    "rerank_score": r.get("rerank_score"),
                },
            ))
        return docs


def get_hierarchical_retriever(k=3, window=2):
    return HierarchicalRetriever(k=k, window=window)