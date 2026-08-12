"""
vector_store.py

Wraps a persistent ChromaDB collection. Kept deliberately small - insert
chunks with their embeddings, query by embedding (+ optional metadata
filter), get text and metadata back out. Swap this module for pgvector
or Pinecone later without touching retrieval.py, as long as the
query_similar() signature stays the same.
"""

from pathlib import Path
import chromadb

from src.chunking import Chunk


class VectorStore:
    def __init__(self, persist_dir: str = "data/vector_store", collection_name: str = "corpus"):
        Path(persist_dir).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_chunks(self, chunks: list[Chunk], embeddings) -> None:
        if not chunks:
            return
        self.collection.upsert(
            ids=[c.chunk_id for c in chunks],
            embeddings=[e.tolist() for e in embeddings],
            documents=[c.text for c in chunks],
            metadatas=[{**c.metadata, "source": c.source} for c in chunks],
        )

    def query_similar(self, query_embedding, top_k: int = 5, where: dict | None = None):
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            where=where,
        )
        hits = []
        for doc, meta, dist, cid in zip(
            results["documents"][0], results["metadatas"][0],
            results["distances"][0], results["ids"][0],
        ):
            hits.append({
                "chunk_id": cid,
                "text": doc,
                "metadata": meta,
                "score": 1 - dist,  # chroma returns distance; flip to similarity
            })
        return hits

    def count(self) -> int:
        return self.collection.count()


if __name__ == "__main__":
    store = VectorStore()
    print(f"collection has {store.count()} chunks stored")
