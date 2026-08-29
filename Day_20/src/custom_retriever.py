from pathlib import Path
import time

import chromadb
from sentence_transformers import SentenceTransformer


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TOP_K = 3
COLLECTION_NAME = "day20_custom"


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


def build_custom_vector_store(chunks):

    print("Loading embedding model...")

    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating custom Chroma collection...")

    client = chromadb.Client()

    # Delete old collection if it exists
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME
    )

    print("Creating embeddings...")

    embeddings = model.encode(
        [chunk["text"] for chunk in chunks]
    ).tolist()

    collection.add(
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

    print(f"Added {len(chunks)} chunks to Chroma.")

    return model, collection


def retrieve(query, model, collection, top_k=TOP_K):

    start_time = time.perf_counter()

    query_embedding = model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    elapsed = time.perf_counter() - start_time

    retrieved = []

    for i in range(len(results["documents"][0])):

        retrieved.append({
            "rank": i + 1,
            "source": results["metadatas"][0][i]["source"],
            "chunk_id": results["metadatas"][0][i]["chunk_id"],
            "text": results["documents"][0][i],
            "distance": float(results["distances"][0][i]),
            "score": 1 - float(results["distances"][0][i])
        })

    return retrieved, elapsed