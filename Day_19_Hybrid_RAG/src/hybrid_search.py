from pathlib import Path

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer
import chromadb


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TOP_K = 3
RRF_K = 60


# --------------------------------------------------
# Load documents
# --------------------------------------------------

def load_documents():

    documents = []

    for file_path in DATA_DIR.glob("*.txt"):

        text = file_path.read_text(encoding="utf-8")

        documents.append({
            "source": file_path.name,
            "text": text
        })

    return documents


# --------------------------------------------------
# Create chunks
# --------------------------------------------------

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


# --------------------------------------------------
# BM25
# --------------------------------------------------

def build_bm25(chunks):

    tokenized_chunks = [
        chunk["text"].lower().split()
        for chunk in chunks
    ]

    return BM25Okapi(tokenized_chunks)


def bm25_search(query, bm25, chunks, top_k=TOP_K):

    scores = bm25.get_scores(
        query.lower().split()
    )

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )

    results = []

    for index in ranked_indices[:top_k]:

        results.append({
            "source": chunks[index]["source"],
            "chunk_id": chunks[index]["chunk_id"],
            "text": chunks[index]["text"],
            "score": float(scores[index])
        })

    return results


# --------------------------------------------------
# Vector Search
# --------------------------------------------------

def build_vector_search(chunks):

    print("Loading embedding model...")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating vector database...")

    client = chromadb.Client()

    collection = client.get_or_create_collection(
        name="day19_hybrid"
    )

    embeddings = model.encode(
        [chunk["text"] for chunk in chunks]
    ).tolist()

    collection.upsert(
        ids=[
            f"{chunk['source']}_{chunk['chunk_id']}"
            for chunk in chunks
        ],
        embeddings=embeddings,
        documents=[
            chunk["text"]
            for chunk in chunks
        ],
        metadatas=[
            {
                "source": chunk["source"],
                "chunk_id": chunk["chunk_id"]
            }
            for chunk in chunks
        ]
    )

    return model, collection


def vector_search(
    query,
    model,
    collection,
    top_k=TOP_K
):

    query_embedding = model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    vector_results = []

    for i in range(len(results["documents"][0])):

        vector_results.append({
            "source": results["metadatas"][0][i]["source"],
            "chunk_id": results["metadatas"][0][i]["chunk_id"],
            "text": results["documents"][0][i],
            "score": 1 - results["distances"][0][i]
        })

    return vector_results


# --------------------------------------------------
# RRF
# --------------------------------------------------

def reciprocal_rank_fusion(
    bm25_results,
    vector_results,
    k=RRF_K
):

    fused_scores = {}
    documents = {}

    # BM25 ranking
    for rank, result in enumerate(
        bm25_results,
        start=1
    ):

        key = (
            result["source"],
            result["chunk_id"]
        )

        fused_scores[key] = (
            fused_scores.get(key, 0)
            + 1 / (k + rank)
        )

        documents[key] = result


    # Vector ranking
    for rank, result in enumerate(
        vector_results,
        start=1
    ):

        key = (
            result["source"],
            result["chunk_id"]
        )

        fused_scores[key] = (
            fused_scores.get(key, 0)
            + 1 / (k + rank)
        )

        documents[key] = result


    ranked = sorted(
        fused_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    results = []

    for rank, (key, score) in enumerate(
        ranked,
        start=1
    ):

        result = documents[key].copy()

        result["rank"] = rank
        result["rrf_score"] = score

        results.append(result)

    return results


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("=" * 60)
    print("HYBRID SEARCH - BM25 + VECTOR + RRF")
    print("=" * 60)

    documents = load_documents()

    print(
        f"\nLoaded {len(documents)} documents."
    )

    chunks = create_chunks(documents)

    print(
        f"Created {len(chunks)} chunks."
    )

    # BM25
    print("\nBuilding BM25 index...")

    bm25 = build_bm25(chunks)

    # Vector
    model, collection = build_vector_search(
        chunks
    )

    print("\nHybrid search ready.")

    print("\nType 'exit' to quit.")

    while True:

        query = input(
            "\nEnter your question: "
        ).strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        # BM25
        bm25_results = bm25_search(
            query,
            bm25,
            chunks
        )

        # Vector
        vector_results = vector_search(
            query,
            model,
            collection
        )

        # RRF
        hybrid_results = reciprocal_rank_fusion(
            bm25_results,
            vector_results
        )

        print("\n" + "=" * 60)
        print("BM25 RESULTS")
        print("=" * 60)

        for rank, result in enumerate(
            bm25_results,
            start=1
        ):

            print(
                f"{rank}. "
                f"{result['source']} | "
                f"chunk {result['chunk_id']} | "
                f"score={result['score']:.4f}"
            )

        print("\n" + "=" * 60)
        print("VECTOR RESULTS")
        print("=" * 60)

        for rank, result in enumerate(
            vector_results,
            start=1
        ):

            print(
                f"{rank}. "
                f"{result['source']} | "
                f"chunk {result['chunk_id']} | "
                f"score={result['score']:.4f}"
            )

        print("\n" + "=" * 60)
        print("HYBRID RESULTS - RRF")
        print("=" * 60)

        for result in hybrid_results[:TOP_K]:

            print(
                f"{result['rank']}. "
                f"{result['source']} | "
                f"chunk {result['chunk_id']} | "
                f"RRF={result['rrf_score']:.6f}"
            )


if __name__ == "__main__":
    main()