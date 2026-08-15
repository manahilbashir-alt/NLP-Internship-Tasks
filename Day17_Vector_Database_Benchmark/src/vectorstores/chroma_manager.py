import json
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CHROMA_DIR = BASE_DIR / "data" / "chroma"
CHUNK_DIR = BASE_DIR / "data" / "chunks"

COLLECTION_NAME = "document_chunks"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# ============================================================
# CHROMA CLIENT
# ============================================================

def get_client():

    return chromadb.PersistentClient(
        path=str(CHROMA_DIR)
    )


# ============================================================
# LIST COLLECTIONS
# ============================================================

def list_collections():

    client = get_client()

    collections = client.list_collections()

    print("\nCollections:")

    if not collections:
        print("No collections found.")
        return

    for collection in collections:
        print(f"- {collection.name}")


# ============================================================
# COUNT DOCUMENTS
# ============================================================

def count_documents():

    client = get_client()

    collection = client.get_collection(
        COLLECTION_NAME
    )

    count = collection.count()

    print(
        f"\nCollection '{COLLECTION_NAME}' "
        f"contains {count} documents."
    )


# ============================================================
# INSPECT COLLECTION
# ============================================================

def inspect_collection(limit=5):

    client = get_client()

    collection = client.get_collection(
        COLLECTION_NAME
    )

    results = collection.get(
        limit=limit,
        include=[
            "documents",
            "metadatas"
        ]
    )

    print(
        f"\nShowing {len(results['ids'])} documents:"
    )

    for i, document_id in enumerate(results["ids"]):

        print("\n" + "-" * 60)

        print(f"ID: {document_id}")

        print(
            f"Text: "
            f"{results['documents'][i][:300]}"
        )

        print(
            f"Metadata: "
            f"{results['metadatas'][i]}"
        )


# ============================================================
# DELETE COLLECTION
# ============================================================

def delete_collection():

    client = get_client()

    existing = [
        collection.name
        for collection in client.list_collections()
    ]

    if COLLECTION_NAME not in existing:

        print(
            f"\nCollection '{COLLECTION_NAME}' "
            "does not exist."
        )

        return

    client.delete_collection(
        COLLECTION_NAME
    )

    print(
        f"\nDeleted collection: "
        f"{COLLECTION_NAME}"
    )


# ============================================================
# LOAD NEW CHUNKS
# ============================================================

def load_chunks_from_file(filename):

    file_path = CHUNK_DIR / filename

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as f:

        data = json.load(f)

    if isinstance(data, list):
        return data

    if isinstance(data, dict):

        if "chunks" in data:
            return data["chunks"]

        return [data]

    return []


# ============================================================
# CLEAN METADATA
# ============================================================

def clean_metadata(metadata):

    clean = {}

    for key, value in metadata.items():

        if value is None:
            clean[key] = "None"

        elif isinstance(
            value,
            (str, int, float, bool)
        ):
            clean[key] = value

        else:
            clean[key] = str(value)

    return clean


# ============================================================
# INCREMENTALLY ADD DOCUMENTS
# ============================================================

def add_documents(filename, start_index=0):

    client = get_client()

    collection = client.get_collection(
        COLLECTION_NAME
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    chunks = load_chunks_from_file(
        filename
    )

    chunks = chunks[start_index:]

    if not chunks:

        print("No new chunks to add.")

        return

    texts = [
        chunk.get("text", "")
        for chunk in chunks
    ]

    metadatas = [
        clean_metadata(
            chunk.get("metadata", {})
        )
        for chunk in chunks
    ]

    # Use a filename-based ID so incremental
    # additions don't conflict with existing IDs.
    ids = [
        f"{filename}_{start_index + i}"
        for i in range(len(chunks))
    ]

    print(
        f"\nAdding {len(chunks)} documents..."
    )

    embeddings = model.encode(
        texts,
        batch_size=32,
        normalize_embeddings=True,
        show_progress_bar=True
    ).tolist()

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )

    print(
        f"Added {len(chunks)} documents."
    )

    print(
        f"New collection count: "
        f"{collection.count()}"
    )


# ============================================================
# COMMAND LINE MENU
# ============================================================

def main():

    print("\n" + "=" * 60)
    print("CHROMADB COLLECTION MANAGER")
    print("=" * 60)

    print("""
1. List collections
2. Count documents
3. Inspect collection
4. Add documents incrementally
5. Delete collection
""")

    choice = input(
        "Select an option: "
    ).strip()

    if choice == "1":

        list_collections()

    elif choice == "2":

        count_documents()

    elif choice == "3":

        inspect_collection()

    elif choice == "4":

        filename = input(
            "Enter chunk filename: "
        ).strip()

        start = input(
            "Start index [0]: "
        ).strip()

        start_index = (
            int(start)
            if start
            else 0
        )

        add_documents(
            filename,
            start_index
        )

    elif choice == "5":

        confirm = input(
            "Type DELETE to confirm: "
        ).strip()

        if confirm == "DELETE":

            delete_collection()

        else:

            print(
                "Deletion cancelled."
            )

    else:

        print("Invalid option.")


if __name__ == "__main__":
    main()