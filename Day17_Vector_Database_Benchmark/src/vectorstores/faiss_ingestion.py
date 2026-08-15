import json
import time
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CHUNK_DIR = BASE_DIR / "data" / "chunks"
FAISS_DIR = BASE_DIR / "data" / "faiss"

FAISS_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

INDEX_FILE = FAISS_DIR / "document_chunks.index"
METADATA_FILE = FAISS_DIR / "metadata.json"

BATCH_SIZE = 100


# ============================================================
# LOAD CHUNKS
# ============================================================

def load_chunks():

    chunks = []

    for file in sorted(CHUNK_DIR.glob("*.json")):

        print(f"Loading: {file.name}")

        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            chunks.extend(data)

        elif isinstance(data, dict):

            if "chunks" in data:
                chunks.extend(data["chunks"])

            else:
                chunks.append(data)

    return chunks


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("FAISS DOCUMENT INGESTION")
    print("=" * 70)

    chunks = load_chunks()

    print(f"\nTotal chunks: {len(chunks)}")

    texts = [
        chunk.get("text", "")
        for chunk in chunks
    ]

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    print("\nLoading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    # --------------------------------------------------------
    # Generate embeddings
    # --------------------------------------------------------

    print("\nGenerating embeddings...")

    start = time.perf_counter()

    embeddings = model.encode(
        texts,
        batch_size=BATCH_SIZE,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    embedding_time = time.perf_counter() - start

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    print(
        f"\nEmbedding time: "
        f"{embedding_time:.3f} seconds"
    )

    print(
        f"Embedding shape: "
        f"{embeddings.shape}"
    )

    # --------------------------------------------------------
    # Create FAISS index
    # --------------------------------------------------------

    dimension = embeddings.shape[1]

    print(
        f"\nCreating FAISS index "
        f"with dimension {dimension}..."
    )

    # Because embeddings are normalized,
    # inner product = cosine similarity.
    index = faiss.IndexFlatIP(dimension)

    # --------------------------------------------------------
    # Add vectors
    # --------------------------------------------------------

    start = time.perf_counter()

    index.add(embeddings)

    index_time = time.perf_counter() - start

    print(
        f"FAISS indexing time: "
        f"{index_time:.6f} seconds"
    )

    print(
        f"Vectors in index: "
        f"{index.ntotal}"
    )

    # --------------------------------------------------------
    # Save index
    # --------------------------------------------------------

    faiss.write_index(
        index,
        str(INDEX_FILE)
    )

    print(
        f"\nIndex saved to:\n{INDEX_FILE}"
    )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    metadata = []

    for i, chunk in enumerate(chunks):

        metadata.append({
            "id": f"chunk_{i}",
            "text": chunk.get("text", ""),
            "metadata": chunk.get(
                "metadata",
                {}
            )
        })

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            metadata,
            f,
            ensure_ascii=False,
            indent=2
        )

    print(
        f"Metadata saved to:\n{METADATA_FILE}"
    )

    # --------------------------------------------------------
    # Test search
    # --------------------------------------------------------

    query = "Who is Mr. Bingley?"

    print(
        f"\nTest query: {query}"
    )

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    start = time.perf_counter()

    distances, indices = index.search(
        query_embedding,
        3
    )

    query_time = time.perf_counter() - start

    print(
        f"FAISS query time: "
        f"{query_time * 1000:.4f} ms"
    )

    print("\nTop 3 results:")

    for rank, idx in enumerate(
        indices[0],
        start=1
    ):

        result = metadata[idx]

        print("\n" + "-" * 60)

        print(f"Result {rank}")
        print(f"ID: {result['id']}")
        print(
            f"Source: "
            f"{result['metadata'].get('source_filename')}"
        )
        print(
            f"Page: "
            f"{result['metadata'].get('page_number')}"
        )
        print(
            f"Chunk: "
            f"{result['metadata'].get('chunk_index')}"
        )
        print(
            f"Similarity: "
            f"{distances[0][rank - 1]:.4f}"
        )
        print(
            result["text"][:500]
        )


if __name__ == "__main__":
    main()