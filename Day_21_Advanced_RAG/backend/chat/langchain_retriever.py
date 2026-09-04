import sys
import json
from pathlib import Path
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from pydantic import PrivateAttr

# --- Paths (relative to this file, inside backend/chat/) ---
BACKEND_ROOT = Path(__file__).resolve().parent.parent
FAISS_DIR = BACKEND_ROOT / "vectorstores" / "FAISS_db"
INDEX_PATH = FAISS_DIR / "index.faiss"
METADATA_PATH = FAISS_DIR / "metadata.json"

EMBEDDING_MODEL = "BAAI/bge-large-en-v1.5"   # must match what built the FAISS index


class FAISSRetriever(BaseRetriever):
    """LangChain-compatible retriever wrapping our own FAISS index +
    metadata.json (built by vectorstores/faiss_manager.py)."""

    k: int = 3
    _model: object = PrivateAttr()
    _index: object = PrivateAttr()
    _row_metadata: list = PrivateAttr()

    def __init__(self, k=3, **kwargs):
        super().__init__(k=k, **kwargs)
        print(f"[langchain_retriever] Loading embedding model ({EMBEDDING_MODEL})...")
        self._model = SentenceTransformer(EMBEDDING_MODEL)
        self._index = faiss.read_index(str(INDEX_PATH))
        self._row_metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    def _get_relevant_documents(self, query: str) -> list[Document]:
        query_vector = self._model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        ).astype("float32")

        scores, row_indices = self._index.search(query_vector, self.k)

        docs = []
        for row_idx, score in zip(row_indices[0], scores[0]):
            if row_idx == -1:
                continue
            meta = self._row_metadata[row_idx]
            docs.append(Document(
                page_content=meta.get("content", ""),
                metadata={
                    "chunk_id": meta.get("chunk_id"),
                    "source_file": meta.get("source_file"),
                    "page_no": meta.get("page_no"),
                    "section": meta.get("section"),
                    "chunk_type": meta.get("chunk_type"),
                    "score": float(score),
                },
            ))
        return docs
    def search_raw(self, query: str, k: int = 10) -> list:
        """Same as _get_relevant_documents but returns plain dicts
        (chunk_id, content) — used by hybrid search's RRF fusion."""
        query_vector = self._model.encode(
            [query], normalize_embeddings=True, convert_to_numpy=True
        ).astype("float32")
        scores, row_indices = self._index.search(query_vector, k)
        results = []
        for row_idx, score in zip(row_indices[0], scores[0]):
            if row_idx == -1:
                continue
            meta = self._row_metadata[row_idx]
            results.append({
                "chunk_id": meta.get("chunk_id"),
                "content": meta.get("content", ""),
                "score": float(score),
            })
        return results

   
    
    def reload(self):
        """Re-reads index.faiss and metadata.json from disk — call this
        after add_document() so newly ingested chunks are searchable
        without restarting the server."""
        self._index = faiss.read_index(str(INDEX_PATH))
        self._row_metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

def get_langchain_retriever(k=3):
    return FAISSRetriever(k=k)


if __name__ == "__main__":
    retriever = get_langchain_retriever(k=6)
    query = "explain support vector machines"
    results = retriever.invoke(query)

    print(f"\nQuery: \"{query}\"\n")
    for rank, doc in enumerate(results, start=1):
        print(f"#{rank}  score={doc.metadata['score']:.4f}  "
              f"[{doc.metadata['source_file']}, page {doc.metadata['page_no']}]")
        print(f"     \"{doc.page_content[:100]}...\"\n")