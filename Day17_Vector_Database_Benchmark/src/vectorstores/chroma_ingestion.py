import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CHUNK_DIR = BASE_DIR / "data" / "chunks"
CHROMA_DIR = BASE_DIR / "data" / "chroma"


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

COLLECTION_NAME = "document_chunks"

BATCH_SIZE = 100


# ============================================================
# LOAD CHUNKS
# ============================================================

def load_chunks():

    chunks = []

    for file in sorted(CHUNK_DIR.glob("*.json")):

        print(f"Loading {file.name}")

        with open(file, "r", encoding="utf-8") as f:
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
# CREATE SAFE METADATA
# ============================================================

def prepare_metadata(metadata):

    clean = {}

    for key, value in metadata.items():

        # Chroma metadata values must be simple scalar types.
        if value is None:
            clean[key] = "None"

        elif isinstance(value, (str, int, float, bool)):
            clean[key] = value

        else:
            clean[key] = str(value)

    return clean


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("CHROMADB DOCUMENT INGESTION")
    print("=" * 70)

    # --------------------------------------------------------
    # Load chunks
    # --------------------------------------------------------

    chunks = load_chunks()

    print(f"\nTotal chunks: {len(chunks)}")

    # --------------------------------------------------------
    # Load embedding model
    # --------------------------------------------------------

    print("\nLoading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    # --------------------------------------------------------
    # Create Chroma client
    # --------------------------------------------------------

    print("\nCreating ChromaDB client...")

    client = chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )

    # --------------------------------------------------------
    # Create/reset collection
    # --------------------------------------------------------

    try:
        client.delete_collection(COLLECTION_NAME)
        print("Existing collection deleted.")
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={
            "description": "Day 17 document chunk embeddings"
        }
    )

    print(f"Collection created: {COLLECTION_NAME}")

    # --------------------------------------------------------
    # Process batches
    # --------------------------------------------------------

    total = len(chunks)

    for start in range(0, total, BATCH_SIZE):

        batch = chunks[start:start + BATCH_SIZE]

        texts = [
            chunk.get("text", "")
            for chunk in batch
        ]

        metadata = [
            prepare_metadata(
                chunk.get("metadata", {})
            )
            for chunk in batch
        ]

        # Unique IDs
        ids = [
            f"chunk_{start + i}"
            for i in range(len(batch))
        ]

        print(
            f"Embedding chunks "
            f"{start + 1}-{min(start + BATCH_SIZE, total)} "
            f"of {total}"
        )

        embeddings = model.encode(
            texts,
            batch_size=32,
            normalize_embeddings=True,
            show_progress_bar=False
        ).tolist()

        collection.add(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadata
        )

    # --------------------------------------------------------
    # Verify
    # --------------------------------------------------------

    count = collection.count()

    print("\n" + "=" * 70)
    print("CHROMADB INGESTION COMPLETE")
    print("=" * 70)

    print(f"Collection: {COLLECTION_NAME}")
    print(f"Documents stored: {count}")

    # --------------------------------------------------------
    # Test query
    # --------------------------------------------------------

    query = "Who is Mr. Bingley?"

    print(f"\nTest query: {query}")

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=3
    )

    print("\nTop 3 results:")

    for i, document in enumerate(
        results["documents"][0],
        start=1
    ):

        metadata = results["metadatas"][0][i - 1]

        print("\n" + "-" * 60)
        print(f"Result {i}")
        print(f"Source: {metadata.get('source_filename')}")
        print(f"Page: {metadata.get('page_number')}")
        print(f"Chunk: {metadata.get('chunk_index')}")
        print(document[:500])


if __name__ == "__main__":
    main()