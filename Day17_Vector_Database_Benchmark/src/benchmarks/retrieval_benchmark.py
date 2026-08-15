import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CHUNK_DIR = BASE_DIR / "data" / "chunks"

OUTPUT_DIR = BASE_DIR / "output" / "benchmarks"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# MODELS
# ============================================================

MODELS = {
    "all-MiniLM-L6-v2":
        "sentence-transformers/all-MiniLM-L6-v2",

    "all-mpnet-base-v2":
        "sentence-transformers/all-mpnet-base-v2",

    "bge-large-en-v1.5":
        "BAAI/bge-large-en-v1.5",
}


# ============================================================
# 20 FACTUAL QUESTIONS
# ============================================================

QUESTIONS = [
    {
        "question": "Who is Mr. Bingley?",
        "keywords": ["Bingley", "young man", "fortune"]
    },
    {
        "question": "Who is Elizabeth Bennet?",
        "keywords": ["Elizabeth", "Bennet"]
    },
    {
        "question": "Who is Jane Bennet?",
        "keywords": ["Jane", "Bennet"]
    },
    {
        "question": "Who is Mr. Bennet married to?",
        "keywords": ["Mrs. Bennet", "wife"]
    },
    {
        "question": "Where does Mr. Bingley move?",
        "keywords": ["Netherfield", "Park"]
    },
    {
        "question": "What is Netherfield Park?",
        "keywords": ["Netherfield", "house", "estate"]
    },
    {
        "question": "How wealthy is Mr. Bingley?",
        "keywords": ["four", "five", "thousand", "year"]
    },
    {
        "question": "Why is Mrs. Bennet excited about Mr. Bingley?",
        "keywords": ["daughters", "marry", "fortune"]
    },
    {
        "question": "Who tells Mrs. Bennet that Netherfield has been rented?",
        "keywords": ["Mrs. Long"]
    },
    {
        "question": "What is Mr. Bennet's reaction to hearing about Mr. Bingley?",
        "keywords": ["Mr. Bennet"]
    },
    {
        "question": "Is Mr. Bingley married?",
        "keywords": ["single"]
    },
    {
        "question": "Where did Mr. Bingley come from?",
        "keywords": ["north", "England"]
    },
    {
        "question": "Who is Mr. Darcy?",
        "keywords": ["Darcy"]
    },
    {
        "question": "What is Mr. Darcy's relationship with Mr. Bingley?",
        "keywords": ["Darcy", "Bingley"]
    },
    {
        "question": "What does Mrs. Bennet hope will happen to her daughters?",
        "keywords": ["marrying", "daughters"]
    },
    {
        "question": "Who is Mr. Collins?",
        "keywords": ["Mr. Collins"]
    },
    {
        "question": "What is Mr. Collins's relationship to the Bennet family?",
        "keywords": ["cousin", "Bennet"]
    },
    {
        "question": "What does Mr. Bennet think about his wife's excitement?",
        "keywords": ["Mr. Bennet", "wife"]
    },
    {
        "question": "What does Mr. Bingley take possession of?",
        "keywords": ["Netherfield", "possession"]
    },
    {
        "question": "Who are the Bennet daughters?",
        "keywords": ["Bennet", "daughters"]
    },
]


# ============================================================
# LOAD CHUNKS
# ============================================================

def load_chunks():

    chunks = []

    for file in sorted(
        CHUNK_DIR.glob("*.json")
    ):

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

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
# PRECISION CALCULATION
# ============================================================

def is_relevant(text, keywords):

    text_lower = text.lower()

    matches = 0

    for keyword in keywords:

        if keyword.lower() in text_lower:
            matches += 1

    # At least half of the expected keywords
    # must appear in the retrieved chunk.
    required = max(
        1,
        len(keywords) // 2
    )

    return matches >= required


# ============================================================
# BENCHMARK MODEL
# ============================================================

def benchmark_model(
    model_name,
    model_path,
    chunks
):

    print("\n" + "=" * 70)
    print(f"MODEL: {model_name}")
    print("=" * 70)

    texts = [
        chunk.get("text", "")
        for chunk in chunks
    ]

    print("Loading model...")

    model = SentenceTransformer(
        model_path
    )

    print("Creating document embeddings...")

    start = time.perf_counter()

    document_embeddings = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=True
    )

    document_time = (
        time.perf_counter() - start
    )

    document_embeddings = np.asarray(
        document_embeddings,
        dtype="float32"
    )

    results = []

    correct_retrievals = 0

    print("\nRunning 20 questions...")

    for question_data in QUESTIONS:

        question = question_data[
            "question"
        ]

        keywords = question_data[
            "keywords"
        ]

        start = time.perf_counter()

        query_embedding = model.encode(
            [question],
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        similarities = (
            document_embeddings
            @ query_embedding[0]
        )

        top_indices = np.argsort(
            similarities
        )[-3:][::-1]

        query_time = (
            time.perf_counter() - start
        )

        relevant = 0

        for index in top_indices:

            text = texts[index]

            if is_relevant(
                text,
                keywords
            ):
                relevant += 1

        precision = relevant / 3

        correct_retrievals += relevant

        results.append({

            "model": model_name,

            "question": question,

            "top1_source":
                chunks[top_indices[0]]
                .get("metadata", {})
                .get("source_filename"),

            "top1_chunk":
                chunks[top_indices[0]]
                .get("metadata", {})
                .get("chunk_index"),

            "relevant_top3":
                relevant,

            "top3_precision":
                round(
                    precision,
                    4
                ),

            "query_time_ms":
                round(
                    query_time * 1000,
                    4
                )
        })

    average_precision = (
        sum(
            r["top3_precision"]
            for r in results
        )
        / len(results)
    )

    average_query_time = (
        sum(
            r["query_time_ms"]
            for r in results
        )
        / len(results)
    )

    print(
        f"\nAverage Top-3 Precision: "
        f"{average_precision:.4f}"
    )

    print(
        f"Average Query Time: "
        f"{average_query_time:.4f} ms"
    )

    return results


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("20-QUESTION RETRIEVAL BENCHMARK")
    print("=" * 70)

    chunks = load_chunks()

    print(
        f"\nTotal document chunks: "
        f"{len(chunks)}"
    )

    all_results = []

    for model_name, model_path in MODELS.items():

        results = benchmark_model(
            model_name,
            model_path,
            chunks
        )

        all_results.extend(
            results
        )

    # --------------------------------------------------------
    # Save detailed results
    # --------------------------------------------------------

    df = pd.DataFrame(
        all_results
    )

    detailed_file = (
        OUTPUT_DIR
        / "retrieval_detailed_results.csv"
    )

    df.to_csv(
        detailed_file,
        index=False
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    summary = (
        df.groupby("model")
        .agg(
            average_top3_precision=(
                "top3_precision",
                "mean"
            ),
            average_query_time_ms=(
                "query_time_ms",
                "mean"
            ),
            total_relevant_top3=(
                "relevant_top3",
                "sum"
            )
        )
        .reset_index()
    )

    summary[
        "precision_percent"
    ] = (
        summary[
            "average_top3_precision"
        ] * 100
    )

    summary_file = (
        OUTPUT_DIR
        / "retrieval_summary.csv"
    )

    summary.to_csv(
        summary_file,
        index=False
    )

    print("\n" + "=" * 70)
    print("FINAL RETRIEVAL RESULTS")
    print("=" * 70)

    print(
        summary.to_string(
            index=False
        )
    )

    print(
        f"\nDetailed results:\n"
        f"{detailed_file}"
    )

    print(
        f"\nSummary:\n"
        f"{summary_file}"
    )


if __name__ == "__main__":
    main()