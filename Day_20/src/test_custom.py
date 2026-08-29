from custom_retriever import (
    load_documents,
    create_chunks,
    build_custom_vector_store,
    retrieve
)


def main():

    print("=" * 70)
    print("DAY 20 - CUSTOM CHROMA RETRIEVER TEST")
    print("=" * 70)

    documents = load_documents()

    print(f"\nLoaded documents: {len(documents)}")

    chunks = create_chunks(documents)

    print(f"Created chunks: {len(chunks)}")

    model, collection = build_custom_vector_store(chunks)

    query = "What is ChromaDB?"

    print(f"\nQuery: {query}")

    results, elapsed = retrieve(
        query,
        model,
        collection
    )

    print(f"\nRetrieval time: {elapsed:.6f} seconds")

    print("\nRetrieved Results:")

    for result in results:

        print("\n" + "-" * 60)

        print(
            f"Rank: {result['rank']}"
        )

        print(
            f"Source: {result['source']}"
        )

        print(
            f"Chunk ID: {result['chunk_id']}"
        )

        print(
            f"Score: {result['score']:.4f}"
        )

        print(
            f"Text: {result['text']}"
        )


if __name__ == "__main__":
    main()