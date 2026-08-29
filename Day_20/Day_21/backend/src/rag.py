from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_PATH = (
    Path(__file__).parent.parent / "data" / "chroma_db"
)

CHROMA_PATH.mkdir(
    parents=True,
    exist_ok=True
)


client = chromadb.PersistentClient(
    path=str(CHROMA_PATH)
)


collection = client.get_or_create_collection(
    name="day21_documents"
)


embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def add_documents(
    chunks: list[str],
    filename: str
):
    if not chunks:
        return 0

    embeddings = embedding_model.encode(
        chunks,
        normalize_embeddings=True
    ).tolist()

    ids = []
    metadatas = []

    for index, chunk in enumerate(chunks):

        ids.append(
            f"{filename}_{index}"
        )

        metadatas.append(
            {
                "source": filename,
                "chunk_id": index
            }
        )

    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def get_sources():

    data = collection.get(
        include=["metadatas"]
    )

    source_counts = {}

    for metadata in data["metadatas"]:

        source = metadata.get(
            "source",
            "unknown"
        )

        source_counts[source] = (
            source_counts.get(source, 0) + 1
        )

    sources = []

    for filename, count in source_counts.items():

        sources.append(
            {
                "filename": filename,
                "chunks": count
            }
        )

    return sources