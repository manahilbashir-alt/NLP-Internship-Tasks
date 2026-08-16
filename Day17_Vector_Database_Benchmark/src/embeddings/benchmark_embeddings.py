import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parents[2]

CHUNK_DIR = BASE_DIR / "data" / "chunks"
OUTPUT_DIR = BASE_DIR / "output" / "embeddings"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


MODELS = {
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
    "bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
}


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

    print(f"\nTotal chunks loaded: {len(chunks)}")

    return chunks


def extract_text(chunk):

    if isinstance(chunk, str):
        return chunk

    return (
        chunk.get("text")
        or chunk.get("content")
        or chunk.get("page_content")
        or ""
    )


def benchmark_model(model_name, model_path, texts):

    print("\n" + "=" * 70)
    print(f"MODEL: {model_name}")
    print("=" * 70)

    print("Loading model...")

    start_load = time.perf_counter()

    model = SentenceTransformer(model_path)

    load_time = time.perf_counter() - start_load

    print(f"Model loading time: {load_time:.2f} seconds")

    print("Generating embeddings...")

    start_embedding = time.perf_counter()

    embeddings = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embedding_time = time.perf_counter() - start_embedding

    embeddings = np.asarray(embeddings)

    print(f"Embedding time: {embedding_time:.2f} seconds")
    print(f"Embedding shape: {embeddings.shape}")

    safe_name = model_name.replace("/", "_")

    output_file = OUTPUT_DIR / f"{safe_name}.npy"

    np.save(output_file, embeddings)

    print(f"Saved: {output_file}")

    return {
        "model": model_name,
        "model_path": model_path,
        "chunks": len(texts),
        "dimensions": int(embeddings.shape[1]),
        "load_time_seconds": round(load_time, 3),
        "embedding_time_seconds": round(embedding_time, 3),
        "chunks_per_second": round(
            len(texts) / embedding_time,
            2
        )
    }


def main():

    print("=" * 70)
    print("EMBEDDING MODEL BENCHMARK")
    print("=" * 70)

    chunks = load_chunks()

    texts = [
        extract_text(chunk).strip()
        for chunk in chunks
    ]

    texts = [
        text
        for text in texts
        if text
    ]

    print(f"\nUsable chunks: {len(texts)}")

    results = []

    for model_name, model_path in MODELS.items():

        try:

            result = benchmark_model(
                model_name,
                model_path,
                texts
            )

            results.append(result)

        except Exception as e:

            print(f"\nERROR: {model_name}")
            print(str(e))

    df = pd.DataFrame(results)

    output_csv = OUTPUT_DIR / "embedding_benchmark.csv"

    df.to_csv(
        output_csv,
        index=False
    )

    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)

    print(df.to_string(index=False))

    print("\nResults saved to:")
    print(output_csv)


if __name__ == "__main__":
    main()