"""
Quick smoke test, not a full suite. Run with:
    PYTHONPATH=src python3 -m pytest tests/ -v
or just:
    PYTHONPATH=src python3 tests/test_pipeline.py

Checks the plumbing works, not retrieval quality - that needs a labeled
eval set and belongs in notebooks/, see the eval metrics section in
docs/RAG_STUDY.md.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ingestion import load_corpus
from chunking import chunk_corpus, recursive_split
from embedding import get_embedder
from vector_store import VectorStore
from retrieval import HybridRetriever


def test_ingestion_reads_sample_corpus():
    docs = load_corpus("data/corpus")
    assert len(docs) >= 1
    assert docs[0].text.strip() != ""


def test_chunking_respects_max_len():
    text = "word " * 500
    chunks = recursive_split(text, max_len=200)
    assert all(len(c) <= 220 for c in chunks)  # small slack for overlap-free split boundary
    assert len(chunks) > 1


def test_chunking_never_drops_content_shorter_than_max():
    short_text = "This fits in one chunk."
    chunks = recursive_split(short_text, max_len=800)
    assert chunks == [short_text]


def test_full_pipeline_returns_relevant_chunk():
    docs = load_corpus("data/corpus")
    chunks = chunk_corpus(docs, max_len=500, overlap_chars=80)
    embedder = get_embedder()
    embeddings = embedder.embed([c.text for c in chunks])

    store = VectorStore(persist_dir="data/vector_store_test", collection_name="test")
    store.add_chunks(chunks, embeddings)

    retriever = HybridRetriever(store, embedder, chunks)
    hits = retriever.retrieve("annual plan refund window", top_k=2)

    assert len(hits) > 0
    # BM25 alone should catch "annual" + "refund" even with the fallback embedder
    assert any("annual" in h["text"].lower() for h in hits)


if __name__ == "__main__":
    test_ingestion_reads_sample_corpus()
    test_chunking_respects_max_len()
    test_chunking_never_drops_content_shorter_than_max()
    test_full_pipeline_returns_relevant_chunk()
    print("all smoke tests passed")
