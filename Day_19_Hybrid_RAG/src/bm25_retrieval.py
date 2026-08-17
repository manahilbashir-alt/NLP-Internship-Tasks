from pathlib import Path

from rank_bm25 import BM25Okapi


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
TOP_K = 3


def load_documents():
    documents = []

    for file_path in DATA_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": file_path.name,
            "text": text
        })

    return documents


def create_chunks(documents):
    chunks = []

    for document in documents:
        paragraphs = [
            paragraph.strip()
            for paragraph in document["text"].split("\n\n")
            if paragraph.strip()
        ]

        for chunk_id, paragraph in enumerate(paragraphs):
            chunks.append({
                "text": paragraph,
                "source": document["source"],
                "chunk_id": chunk_id
            })

    return chunks


def tokenize(text):
    return text.lower().split()


def build_bm25(chunks):
    tokenized_chunks = [
        tokenize(chunk["text"])
        for chunk in chunks
    ]

    return BM25Okapi(tokenized_chunks)


def retrieve_bm25(query, bm25, chunks, top_k=TOP_K):
    query_tokens = tokenize(query)

    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True
    )

    results = []

    for index in ranked_indices[:top_k]:
        results.append({
            "rank": len(results) + 1,
            "score": float(scores[index]),
            "source": chunks[index]["source"],
            "chunk_id": chunks[index]["chunk_id"],
            "text": chunks[index]["text"]
        })

    return results


def main():
    print("=" * 60)
    print("BM25 RETRIEVAL")
    print("=" * 60)

    print("\nLoading documents...")

    documents = load_documents()

    print(f"Loaded {len(documents)} document(s).")

    print("Creating chunks...")

    chunks = create_chunks(documents)

    print(f"Created {len(chunks)} chunks.")

    print("Building BM25 index...")

    bm25 = build_bm25(chunks)

    print("BM25 index ready.")

    print("\nType 'exit' to quit.")

    while True:
        query = input("\nEnter your question: ").strip()

        if query.lower() == "exit":
            print("Exiting BM25 retrieval.")
            break

        if not query:
            continue

        results = retrieve_bm25(
            query,
            bm25,
            chunks,
            top_k=TOP_K
        )

        print("\n" + "=" * 60)
        print("BM25 RETRIEVED RESULTS")
        print("=" * 60)

        for result in results:
            print(f"\nResult #{result['rank']}")
            print(f"BM25 score: {result['score']:.4f}")
            print(f"Source: {result['source']}")
            print(f"Chunk ID: {result['chunk_id']}")

            print("\nText:")
            print(result["text"])

            print("-" * 60)


if __name__ == "__main__":
    main()