"""
embedding.py

Thin wrapper around sentence-transformers. Default model is
all-MiniLM-L6-v2 - small, fast, good enough for most internal-docs use
cases. Swap in bge-large or e5-large if retrieval quality on your corpus
needs it; just re-embed everything if you change models, embeddings
from different models aren't comparable.

Note: this sandbox has no route to huggingface.co, so if the real model
can't download, we drop to a hashing-based stand-in purely so the rest
of the pipeline can be exercised end-to-end here. Swap EMBEDDER back to
SentenceTransformerEmbedder in any environment with real network access
- that's the one meant for production.
"""

import hashlib
import numpy as np


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> np.ndarray:
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)


class OfflineHashEmbedder:
    """
    Deterministic bag-of-words hashing embedder. This is NOT a real
    semantic embedder - it can't tell "car" and "automobile" are related.
    It exists only so ingestion -> chunking -> embedding -> vector store
    -> retrieval can be run and sanity-checked without a network call to
    a model hub. Do not ship this.
    """
    def __init__(self, dim: int = 384):
        self.model_name = "offline-hash-fallback"
        self.dim = dim

    def embed(self, texts: list[str]) -> np.ndarray:
        vecs = np.zeros((len(texts), self.dim), dtype=np.float32)
        for i, text in enumerate(texts):
            for word in text.lower().split():
                h = int(hashlib.md5(word.encode()).hexdigest(), 16)
                vecs[i, h % self.dim] += 1.0
            norm = np.linalg.norm(vecs[i])
            if norm > 0:
                vecs[i] /= norm
        return vecs


def get_embedder(model_name: str = "all-MiniLM-L6-v2"):
    try:
        return SentenceTransformerEmbedder(model_name)
    except Exception as e:
        print(f"[embedding] couldn't load '{model_name}' ({e}); "
              f"falling back to OfflineHashEmbedder for this run.")
        return OfflineHashEmbedder()


if __name__ == "__main__":
    embedder = get_embedder()
    vecs = embedder.embed(["a test sentence", "another one, different topic"])
    print(f"model: {embedder.model_name}, shape: {vecs.shape}")
