from pathlib import Path
import csv

from .hybrid_search import (
    load_documents,
    create_chunks,
    build_bm25,
    bm25_search,
    build_vector_search,
    vector_search,
    reciprocal_rank_fusion,
)


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = (
    Path(__file__).resolve().parent.parent
    / "output"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

TOP_K = 3


# ============================================================
# BENCHMARK QUESTIONS
# ============================================================

QUESTIONS = [
    {
        "question": "What is retrieval augmented generation?",
        "keywords": [
            "retrieval",
            "generation",
            "documents"
        ]
    },
    {
        "question": "What are the advantages of vector databases?",
        "keywords": [
            "vector",
            "database",
            "search"
        ]
    },
    {
        "question": "How does BM25 work?",
        "keywords": [
            "bm25",
            "ranking",
            "term"
        ]
    },
    {
        "question": "What is semantic search?",
        "keywords": [
            "semantic",
            "search",
            "meaning"
        ]
    },
    {
        "question": "What are embeddings?",
        "keywords": [
            "embedding",
            "vector",
            "representation"
        ]
    },
    {
        "question": "What is a vector database?",
        "keywords": [
            "vector",
            "database",
            "similarity"
        ]
    },
    {
        "question": "Why is retrieval important in RAG?",
        "keywords": [
            "retrieval",
            "rag",
            "context"
        ]
    },
    {
        "question": "What is hybrid search?",
        "keywords": [
            "hybrid",
            "bm25",
            "vector"
        ]
    },
    {
        "question": "How does semantic similarity work?",
        "keywords": [
            "semantic",
            "similarity",
            "embedding"
        ]
    },
    {
        "question": "Why combine BM25 and vector search?",
        "keywords": [
            "bm25",
            "vector",
            "combine"
        ]
    },
]


# ============================================================
# RELEVANCE CHECK
# ============================================================

def is_relevant(result, keywords):

    text = result["text"].lower()

    matches = sum(
        1
        for keyword in keywords
        if keyword.lower() in text
    )

    return matches >= 1


# ============================================================
# PRECISION
# ============================================================

def calculate_precision(
    results,
    keywords
):

    top_results = results[:TOP_K]

    if not top_results:
        return 0.0

    relevant = sum(
        is_relevant(result, keywords)
        for result in top_results
    )

    return relevant / len(top_results)


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("HYBRID RETRIEVAL BENCHMARK")
    print("BM25 vs VECTOR vs HYBRID RRF")
    print("=" * 70)

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    documents = load_documents()

    chunks = create_chunks(
        documents
    )

    print(
        f"\nDocuments: {len(documents)}"
    )

    print(
        f"Chunks: {len(chunks)}"
    )

    # --------------------------------------------------------
    # Build BM25
    # --------------------------------------------------------

    print(
        "\nBuilding BM25..."
    )

    bm25 = build_bm25(
        chunks
    )

    # --------------------------------------------------------
    # Build vector search
    # --------------------------------------------------------

    print(
        "\nBuilding vector search..."
    )

    model, collection = build_vector_search(
        chunks
    )

    # --------------------------------------------------------
    # Run benchmark
    # --------------------------------------------------------

    results = []

    print(
        "\nRunning benchmark..."
    )

    for number, item in enumerate(
        QUESTIONS,
        start=1
    ):

        question = item["question"]
        keywords = item["keywords"]

        print(
            f"\n[{number}/{len(QUESTIONS)}] "
            f"{question}"
        )

        # BM25
        bm25_results = bm25_search(
            question,
            bm25,
            chunks,
            TOP_K
        )

        # Vector
        vector_results = vector_search(
            question,
            model,
            collection,
            TOP_K
        )

        # Hybrid
        hybrid_results = reciprocal_rank_fusion(
            bm25_results,
            vector_results
        )

        # Precision
        bm25_precision = calculate_precision(
            bm25_results,
            keywords
        )

        vector_precision = calculate_precision(
            vector_results,
            keywords
        )

        hybrid_precision = calculate_precision(
            hybrid_results,
            keywords
        )

        print(
            f"BM25:   {bm25_precision:.2f}"
        )

        print(
            f"Vector: {vector_precision:.2f}"
        )

        print(
            f"Hybrid: {hybrid_precision:.2f}"
        )

        results.append({
            "question": question,
            "bm25_precision": bm25_precision,
            "vector_precision": vector_precision,
            "hybrid_precision": hybrid_precision
        })

    # --------------------------------------------------------
    # Calculate averages
    # --------------------------------------------------------

    count = len(results)

    avg_bm25 = sum(
        row["bm25_precision"]
        for row in results
    ) / count

    avg_vector = sum(
        row["vector_precision"]
        for row in results
    ) / count

    avg_hybrid = sum(
        row["hybrid_precision"]
        for row in results
    ) / count

    # --------------------------------------------------------
    # Save detailed results
    # --------------------------------------------------------

    detailed_file = (
        OUTPUT_DIR
        / "hybrid_retrieval_detailed.csv"
    )

    with open(
        detailed_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=[
                "question",
                "bm25_precision",
                "vector_precision",
                "hybrid_precision"
            ]
        )

        writer.writeheader()

        writer.writerows(
            results
        )

    # --------------------------------------------------------
    # Save summary
    # --------------------------------------------------------

    summary_file = (
        OUTPUT_DIR
        / "hybrid_retrieval_summary.csv"
    )

    with open(
        summary_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.writer(
            file
        )

        writer.writerow([
            "method",
            "average_top3_precision",
            "precision_percent"
        ])

        writer.writerow([
            "BM25",
            round(avg_bm25, 4),
            round(avg_bm25 * 100, 2)
        ])

        writer.writerow([
            "Vector",
            round(avg_vector, 4),
            round(avg_vector * 100, 2)
        ])

        writer.writerow([
            "Hybrid RRF",
            round(avg_hybrid, 4),
            round(avg_hybrid * 100, 2)
        ])

    # --------------------------------------------------------
    # Final output
    # --------------------------------------------------------

    print("\n")
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    print(
        f"\nBM25 Precision:   "
        f"{avg_bm25 * 100:.2f}%"
    )

    print(
        f"Vector Precision: "
        f"{avg_vector * 100:.2f}%"
    )

    print(
        f"Hybrid Precision: "
        f"{avg_hybrid * 100:.2f}%"
    )

    if avg_hybrid > avg_bm25:
        print(
            "\nHybrid search improved "
            "over BM25."
        )

    if avg_hybrid > avg_vector:
        print(
            "Hybrid search improved "
            "over vector search."
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