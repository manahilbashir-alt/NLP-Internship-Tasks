from src.generator import generate_answer
from src.prompt import build_augmented_prompt
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# -----------------------------
# Configuration
# -----------------------------

DOCUMENT_DIR = Path("data/documents")

CHROMA_DIR = "data/chroma_db"

COLLECTION_NAME = "rag_documents"

TOP_K = 3


# -----------------------------
# Load embedding model
# -----------------------------

print("Loading embedding model...")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

print("Embedding model loaded.")


# -----------------------------
# Create ChromaDB
# -----------------------------

client = chromadb.PersistentClient(path=CHROMA_DIR)

collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# -----------------------------
# Read documents
# -----------------------------

documents = []
ids = []
metadatas = []

for file_path in DOCUMENT_DIR.glob("*.txt"):

    text = file_path.read_text(encoding="utf-8")

    # Simple chunking for now
    chunks = [
        text[i:i + 500]
        for i in range(0, len(text), 500)
    ]

    for index, chunk in enumerate(chunks):

        documents.append(chunk)

        ids.append(
            f"{file_path.stem}_{index}"
        )

        metadatas.append(
            {
                "source": file_path.name,
                "chunk_id": index
            }
        )


# -----------------------------
# Create embeddings
# -----------------------------

print(f"Creating embeddings for {len(documents)} chunks...")

embeddings = embedding_model.encode(
    documents
).tolist()


# -----------------------------
# Store in ChromaDB
# -----------------------------

collection.upsert(
    ids=ids,
    documents=documents,
    embeddings=embeddings,
    metadatas=metadatas
)

print("Documents stored in ChromaDB.")


# -----------------------------
# Retrieval function
# -----------------------------

def retrieve(query, top_k=TOP_K):

    print("\nCreating query embedding...")

    query_embedding = embedding_model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k
    )

    return results


# -----------------------------
# CLI test
# -----------------------------
if __name__ == "__main__":

    question = input(
        "\nEnter your question: "
    )

    results = retrieve(question)

    # Build augmented prompt
    augmented_prompt = build_augmented_prompt(
        question,
        results
    )

    print("\n")
    print("=" * 60)
    print("AUGMENTED PROMPT")
    print("=" * 60)

    print(augmented_prompt)

    # Generate grounded answer
    print("\n")
    print("=" * 60)
    print("GENERATING GROUNDED ANSWER...")
    print("=" * 60)

    answer = generate_answer(
        augmented_prompt
    )

    print("\nANSWER:")
    print(answer)

    # Display retrieved results
    print("\n")
    print("=" * 60)
    print("RETRIEVED RESULTS")
    print("=" * 60)

    for i in range(len(results["documents"][0])):

        document = results["documents"][0][i]

        distance = results["distances"][0][i]

        metadata = results["metadatas"][0][i]

        similarity = 1 / (1 + distance)

        print(f"\nResult #{i + 1}")

        print(
            f"Similarity score: {similarity:.4f}"
        )

        print(
            f"Source: {metadata['source']}"
        )

        print(
            f"Chunk ID: {metadata['chunk_id']}"
        )

        print("\nText:")

        print(document)

        print("-" * 60)