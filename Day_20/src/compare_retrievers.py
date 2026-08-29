import sys
from pathlib import Path

# Allow imports from this src folder
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))


from custom_retriever import (
    load_documents as custom_load_documents,
    create_chunks as custom_create_chunks,
    build_custom_vector_store,
    retrieve as custom_retrieve,
)

from langchain_retriever import (
    build_langchain_retriever,
    retrieve as langchain_retrieve,
)


TEST_QUERIES = [
    "What is ChromaDB?",
    "What is a vector database?",
    "What are embeddings?",
    "How does similarity search work?",
    "What is retrieval augmented generation?",
    "How do embeddings help RAG?",
    "What is hybrid search?",
    "How does a RAG system retrieve information?",
    "Why are vector databases useful?",
    "What is the purpose of storing embeddings?",
]


def get_source_chunk_pairs(results):
    """Return source/chunk identifiers for comparison."""

    return {
        (
            result["source"],
            result["chunk_id"]
        )
        for result in results
    }


def print_results(title, results):

    print(f"\n{title}")
    print("-" * 60)

    for result in results:

        print(
            f"{result['rank']}. "
            f"{result['source']} "
            f"(chunk {result['chunk_id']})"
        )


def main():

    print("=" * 80)
    print("DAY 20 - CUSTOM CHROMA VS LANGCHAIN CHROMA")
    print("=" * 80)

    # --------------------------------------------------
    # Load documents
    # --------------------------------------------------

    documents = custom_load_documents()

    chunks = custom_create_chunks(documents)

    print(f"\nDocuments: {len(documents)}")
    print(f"Chunks: {len(chunks)}")

    # --------------------------------------------------
    # Build custom retriever
    # --------------------------------------------------

    print("\nBuilding custom Chroma retriever...")

    custom_model, custom_collection = (
        build_custom_vector_store(chunks)
    )

    # --------------------------------------------------
    # Build LangChain retriever
    # --------------------------------------------------

    print("\nBuilding LangChain Chroma retriever...")

    langchain_retriever = build_langchain_retriever(
        chunks
    )

    # --------------------------------------------------
    # Statistics
    # --------------------------------------------------

    custom_times = []
    langchain_times = []

    overlap_scores = []

    custom_faster_count = 0
    langchain_faster_count = 0

    # --------------------------------------------------
    # Run all queries
    # --------------------------------------------------

    for index, query in enumerate(TEST_QUERIES, start=1):

        print("\n")
        print("#" * 80)
        print(f"QUERY {index}: {query}")
        print("#" * 80)

        # Custom
        custom_results, custom_time = custom_retrieve(
            query,
            custom_model,
            custom_collection,
            top_k=3
        )

        # LangChain
        langchain_results, langchain_time = (
            langchain_retrieve(
                query,
                langchain_retriever
            )
        )

        custom_times.append(custom_time)
        langchain_times.append(langchain_time)

        # --------------------------------------------------
        # Compare retrieved chunks
        # --------------------------------------------------

        custom_sources = get_source_chunk_pairs(
            custom_results
        )

        langchain_sources = get_source_chunk_pairs(
            langchain_results
        )

        overlap = custom_sources.intersection(
            langchain_sources
        )

        overlap_percentage = (
            len(overlap)
            / max(len(custom_sources), 1)
        ) * 100

        overlap_scores.append(
            overlap_percentage
        )

        # --------------------------------------------------
        # Faster implementation
        # --------------------------------------------------

        if custom_time < langchain_time:
            custom_faster_count += 1
        elif langchain_time < custom_time:
            langchain_faster_count += 1

        # --------------------------------------------------
        # Print results
        # --------------------------------------------------

        print_results(
            "CUSTOM CHROMA RESULTS",
            custom_results
        )

        print(
            f"\nCustom retrieval time: "
            f"{custom_time:.6f} seconds"
        )

        print_results(
            "LANGCHAIN CHROMA RESULTS",
            langchain_results
        )

        print(
            f"\nLangChain retrieval time: "
            f"{langchain_time:.6f} seconds"
        )

        print(
            f"\nResult overlap: "
            f"{len(overlap)}/{len(custom_sources)}"
        )

        print(
            f"Overlap percentage: "
            f"{overlap_percentage:.2f}%"
        )

    # --------------------------------------------------
    # Final summary
    # --------------------------------------------------

    avg_custom = sum(custom_times) / len(custom_times)

    avg_langchain = (
        sum(langchain_times)
        / len(langchain_times)
    )

    avg_overlap = (
        sum(overlap_scores)
        / len(overlap_scores)
    )

    print("\n\n")
    print("=" * 80)
    print("FINAL COMPARISON")
    print("=" * 80)

    print(
        f"\nNumber of test queries: "
        f"{len(TEST_QUERIES)}"
    )

    print(
        f"Average custom retrieval time: "
        f"{avg_custom:.6f} seconds"
    )

    print(
        f"Average LangChain retrieval time: "
        f"{avg_langchain:.6f} seconds"
    )

    print(
        f"Average result overlap: "
        f"{avg_overlap:.2f}%"
    )

    print(
        f"Custom retriever faster on: "
        f"{custom_faster_count}/{len(TEST_QUERIES)} queries"
    )

    print(
        f"LangChain retriever faster on: "
        f"{langchain_faster_count}/{len(TEST_QUERIES)} queries"
    )

    print("\nInterpretation:")

    if avg_overlap >= 80:
        print(
            "Both retrievers show strong agreement "
            "on the retrieved chunks."
        )
    else:
        print(
            "The retrievers show noticeable differences "
            "in their retrieved chunks."
        )

    if avg_custom < avg_langchain:
        print(
            "The custom implementation was faster on "
            "average for this experiment."
        )
    elif avg_langchain < avg_custom:
        print(
            "The LangChain implementation was faster on "
            "average for this experiment."
        )
    else:
        print(
            "Both implementations had approximately "
            "the same average retrieval time."
        )

    print("\nTask 1 comparison completed successfully.")


if __name__ == "__main__":
    main()