import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

BENCHMARK_DIR = BASE_DIR / "output" / "benchmarks"


# ------------------------------------------------------------
# Embedding retrieval results
# ------------------------------------------------------------

retrieval_file = (
    BENCHMARK_DIR
    / "retrieval_summary.csv"
)

retrieval = pd.read_csv(
    retrieval_file
)


# ------------------------------------------------------------
# FAISS / Chroma speed results
# ------------------------------------------------------------

speed_file = (
    BENCHMARK_DIR
    / "chroma_vs_faiss_speed.csv"
)

speed = pd.read_csv(
    speed_file
)


# ------------------------------------------------------------
# Calculate vector-store averages
# ------------------------------------------------------------

chroma_ms = speed[
    "chroma_ms"
].mean()

faiss_ms = speed[
    "faiss_ms"
].mean()


# ------------------------------------------------------------
# Create final model table
# ------------------------------------------------------------

final = retrieval[
    [
        "model",
        "precision_percent",
        "average_query_time_ms"
    ]
].copy()


final = final.rename(
    columns={
        "precision_percent":
            "top3_precision_percent",

        "average_query_time_ms":
            "embedding_query_time_ms"
    }
)


# ------------------------------------------------------------
# Add FAISS and ChromaDB measurements
# ------------------------------------------------------------

final[
    "faiss_vector_search_ms"
] = faiss_ms

final[
    "chroma_vector_search_ms"
] = chroma_ms


# ------------------------------------------------------------
# Approximate combined latency
# ------------------------------------------------------------

final[
    "faiss_total_ms"
] = (
    final["embedding_query_time_ms"]
    + faiss_ms
)

final[
    "chroma_total_ms"
] = (
    final["embedding_query_time_ms"]
    + chroma_ms
)


# ------------------------------------------------------------
# Precision / latency ratio
# ------------------------------------------------------------

final[
    "precision_per_ms_faiss"
] = (
    final["top3_precision_percent"]
    / final["faiss_total_ms"]
)


final[
    "precision_per_ms_chroma"
] = (
    final["top3_precision_percent"]
    / final["chroma_total_ms"]
)


# ------------------------------------------------------------
# Round values
# ------------------------------------------------------------

numeric_columns = [
    "top3_precision_percent",
    "embedding_query_time_ms",
    "faiss_vector_search_ms",
    "chroma_vector_search_ms",
    "faiss_total_ms",
    "chroma_total_ms",
    "precision_per_ms_faiss",
    "precision_per_ms_chroma"
]

final[numeric_columns] = final[
    numeric_columns
].round(4)


# ------------------------------------------------------------
# Save
# ------------------------------------------------------------

output_file = (
    BENCHMARK_DIR
    / "final_benchmark_results.csv"
)

final.to_csv(
    output_file,
    index=False
)


# ------------------------------------------------------------
# Display
# ------------------------------------------------------------

print("=" * 80)
print("FINAL EMBEDDING + VECTOR STORE BENCHMARK")
print("=" * 80)

print()

print(
    final.to_string(
        index=False
    )
)

print()

print(
    f"Average ChromaDB search: "
    f"{chroma_ms:.4f} ms"
)

print(
    f"Average FAISS search: "
    f"{faiss_ms:.4f} ms"
)

print()

best_precision = final.loc[
    final["top3_precision_percent"].idxmax()
]

best_faiss_ratio = final.loc[
    final["precision_per_ms_faiss"].idxmax()
]

print(
    "Highest precision model: "
    f"{best_precision['model']} "
    f"({best_precision['top3_precision_percent']}%)"
)

print(
    "Best precision/speed ratio with FAISS: "
    f"{best_faiss_ratio['model']}"
)

print()

print(
    f"Results saved to:\n"
    f"{output_file}"
)