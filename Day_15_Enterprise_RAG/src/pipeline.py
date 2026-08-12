"""
pipeline.py

Full RAG pipeline:

Corpus
    -> Ingestion
    -> Chunking
    -> Embedding
    -> Vector Store
    -> Hybrid Retrieval
    -> Augmented Prompt
    -> LLM
    -> Grounded Response

Usage:
    python -m src.pipeline "What's the refund window on annual plans?"
"""

import sys

from src.ingestion import load_corpus
from src.chunking import chunk_corpus
from src.embedding import get_embedder
from src.vector_store import VectorStore
from src.retrieval import HybridRetriever
from src.llm import generate_grounded_response


def build_prompt(query: str, hits: list[dict]) -> str:
    """
    Build the augmented prompt from retrieved document chunks.
    """

    context_block = "\n\n".join(
        f"[{i + 1}] (source: {h['source']})\n{h['text']}"
        for i, h in enumerate(hits)
    )

    return f"""You are answering a question using only the context below.

Rules:
1. Use only the provided context.
2. Do not guess or use outside knowledge.
3. If the answer is not contained in the context, say:
   "I could not find this information in the provided documents."
4. Cite the relevant source numbers such as [1], [2].

Context:
{context_block}

Question:
{query}

Answer:"""


def run(
    corpus_dir: str = "data/corpus",
    query: str = "",
    top_k: int = 5,
):
    """
    Run the complete RAG pipeline.
    """

    # 1. Ingestion
    print(f"[1/7] Loading corpus from {corpus_dir}")

    docs = load_corpus(corpus_dir)

    print(f"      {len(docs)} document(s) loaded")

    # 2. Chunking
    print("[2/7] Chunking")

    chunks = chunk_corpus(
        docs,
        max_len=500,
        overlap_chars=80,
    )

    print(f"      {len(chunks)} chunk(s) created")

    # 3. Embedding
    print("[3/7] Creating embeddings")

    embedder = get_embedder()

    embeddings = embedder.embed(
        [chunk.text for chunk in chunks]
    )

    print(f"      model: {embedder.model_name}")

    # 4. Vector store
    print("[4/7] Writing to vector store")

    store = VectorStore()

    store.add_chunks(
        chunks,
        embeddings,
    )

    print(f"      store now holds {store.count()} chunk(s)")

    # 5. Hybrid retrieval
    print("[5/7] Hybrid retrieval")

    retriever = HybridRetriever(
        store,
        embedder,
        chunks,
    )

    hits = retriever.retrieve(
        query,
        top_k=top_k,
    )

    print(f"      retrieved {len(hits)} relevant chunk(s)")

    # 6. Augmented prompt
    print("[6/7] Building augmented prompt")

    prompt = build_prompt(
        query,
        hits,
    )

    print("\n--- Retrieved Chunks ---")

    for hit in hits:
        print(
            f"  {hit['chunk_id']} "
            f"(fused score {hit['fused_score']:.4f})"
        )

    print("\n--- Augmented Prompt ---\n")
    print(prompt)

    # 7. LLM grounded response
    print("\n[7/7] Generating grounded response")

    context = "\n\n".join(
        f"[{i + 1}] (source: {hit['source']})\n{hit['text']}"
        for i, hit in enumerate(hits)
    )

    answer = generate_grounded_response(
        question=query,
        context=context,
    )

    print("\n--- GROUNDED RESPONSE ---\n")
    print(answer)

    return answer, hits, prompt


if __name__ == "__main__":
    query = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "What is this document about?"
    )

    run(query=query)