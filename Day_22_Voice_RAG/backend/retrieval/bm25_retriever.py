import json
import re
from pathlib import Path
from rank_bm25 import BM25Okapi

BACKEND_ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = BACKEND_ROOT / "vectorstores" / "FAISS_db" / "metadata.json"


def tokenize(text):
    return re.findall(r"\w+", text.lower())


class BM25Retriever:
    def __init__(self):
        self.chunks = []
        self.bm25 = None
        self.reload()

    def reload(self):
        """(Re)builds the BM25 index from whatever is currently in
        metadata.json — call this after /ingest so new docs are searchable."""
        self.chunks = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
        tokenized_corpus = [tokenize(c["content"]) for c in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def search(self, query: str, top_k: int = 10) -> list:
        query_tokens = tokenize(query)
        scores = self.bm25.get_scores(query_tokens)
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [
            {"chunk_id": self.chunks[i]["chunk_id"],
             "content": self.chunks[i]["content"],
             "score": float(scores[i])}
            for i in ranked
        ]