import json
import time
from pathlib import Path

import chromadb
import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

BENCHMARK_FILE = (
    BASE_DIR
    / "data"
    / "benchmark"
    / "benchmark_chunks.json"
)

CHROMA_DIR = (
    BASE_DIR
    / "data"
    / "chroma_benchmark"
)

FAISS_DIR = (
    BASE_DIR
    / "data"
    / "faiss_benchmark"
)

OUTPUT_DIR = (
    BASE_DIR
    / "output"
    / "benchmarks"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = (
    "sentence-transformers/"
    "all-MiniLM-L6-v2"
)

COLLECTION_NAME = "benchmark_1200"

QUERIES = [
    "Who is Mr. Bingley?",
    "Who is Elizabeth Bennet?",
    "Where does Mr. Darcy live?",
    "Why does Mrs. Bennet want her daughters to marry?",
    "What is Netherfield Park?",
    "Who is Mr. Bennet's wife?",
    "What happens when Mr. Bingley arrives?",
    "What does Elizabeth think of Mr. Darcy?",
    "Who is Jane Bennet?",
    "What is Mr. Collins's relationship to the Bennet family?",
]


# ============================================================
# LOAD DATA
# ============================================================

def load_chunks():

    with open(
        BENCHMARK_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        return json.load(f)


# ============================================================
# CREATE EMBEDDINGS
# ============================================================

def create_embeddings(chunks, model):

    texts = [
        chunk.get("text", "")
        for chunk in chunks
    ]

    print(
        f"\nEmbedding {len(texts)} chunks..."
    )

    start = time.perf_counter()

    embeddings = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    elapsed = time.perf_counter() - start

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    print(
        f"Embedding time: "
        f"{elapsed:.3f} seconds"
    )

    return embeddings


# ============================================================
# CHROMADB
# ============================================================

def setup_chroma(chunks, embeddings):

    print("\nSetting up ChromaDB...")

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    try:
        client.delete_collection(
            COLLECTION_NAME
        )
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    ids = [
        f"benchmark_{i}"
        for i in range(len(chunks))
    ]

    documents = [
        chunk.get("text", "")
        for chunk in chunks
    ]

    metadatas = []

    for chunk in chunks:

        metadata = {}

        for key, value in chunk.get(
            "metadata",
            {}
        ).items():

            if value is None:
                value = "None"

            elif not isinstance(
                value,
                (str, int, float, bool)
            ):
                value = str(value)

            metadata[key] = value

        metadatas.append(metadata)

    start = time.perf_counter()

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas
    )

    ingestion_time = (
        time.perf_counter() - start
    )

    print(
        f"ChromaDB vectors: "
        f"{collection.count()}"
    )

    print(
        f"ChromaDB insertion time: "
        f"{ingestion_time:.3f} seconds"
    )

    return client, collection


# ============================================================
# FAISS
# ============================================================

def setup_faiss(embeddings):

    print("\nSetting up FAISS...")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    start = time.perf_counter()

    index.add(embeddings)

    ingestion_time = (
        time.perf_counter() - start
    )

    print(
        f"FAISS vectors: "
        f"{index.ntotal}"
    )

    print(
        f"FAISS insertion time: "
        f"{ingestion_time:.6f} seconds"
    )

    return index


# ============================================================
# QUERY BENCHMARK
# ============================================================

def benchmark_chroma(
    collection,
    query_embeddings
):

    times = []

    for query_embedding in query_embeddings:

        start = time.perf_counter()

        collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=3
        )

        elapsed = (
            time.perf_counter() - start
        )

        times.append(elapsed * 1000)

    return times


def benchmark_faiss(
    index,
    query_embeddings
):

    times = []

    for query_embedding in query_embeddings:

        query = np.asarray(
            [query_embedding],
            dtype="float32"
        )

        start = time.perf_counter()

        index.search(
            query,
            3
        )

        elapsed = (
            time.perf_counter() - start
        )

        times.append(elapsed * 1000)

    return times


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("CHROMADB vs FAISS SPEED BENCHMARK")
    print("=" * 70)

    chunks = load_chunks()

    print(
        f"\nBenchmark dataset: "
        f"{len(chunks)} chunks"
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    embeddings = create_embeddings(
        chunks,
        model
    )

    # Query embeddings
    query_embeddings = model.encode(
        QUERIES,
        normalize_embeddings=True
    )

    query_embeddings = np.asarray(
        query_embeddings,
        dtype="float32"
    )

    # Setup stores
    _, chroma_collection = setup_chroma(
        chunks,
        embeddings
    )

    faiss_index = setup_faiss(
        embeddings
    )

    # Warm-up
    print("\nWarming up vector stores...")

    chroma_collection.query(
        query_embeddings=[
            query_embeddings[0].tolist()
        ],
        n_results=3
    )

    faiss_index.search(
        np.asarray(
            [query_embeddings[0]],
            dtype="float32"
        ),
        3
    )

    # Benchmark
    print("\nBenchmarking ChromaDB...")

    chroma_times = benchmark_chroma(
        chroma_collection,
        query_embeddings
    )

    print("\nBenchmarking FAISS...")

    faiss_times = benchmark_faiss(
        faiss_index,
        query_embeddings
    )

    # Results
    results = []

    for i, query in enumerate(QUERIES):

        results.append({
            "query": query,
            "chroma_ms": round(
                chroma_times[i],
                4
            ),
            "faiss_ms": round(
                faiss_times[i],
                4
            )
        })

    df = pd.DataFrame(results)

    output_file = (
        OUTPUT_DIR
        / "chroma_vs_faiss_speed.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print("\n" + "=" * 70)
    print("SPEED RESULTS")
    print("=" * 70)

    print(df.to_string(index=False))

    print("\nAverage query time:")

    print(
        f"ChromaDB: "
        f"{df['chroma_ms'].mean():.4f} ms"
    )

    print(
        f"FAISS: "
        f"{df['faiss_ms'].mean():.4f} ms"
    )

    print(
        f"\nResults saved to:\n"
        f"{output_file}"
    )


if __name__ == "__main__":
    main()