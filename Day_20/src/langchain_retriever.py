from pathlib import Path
import time

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


DATA_DIR = Path(__file__).resolve().parent.parent / "data"

TOP_K = 3
COLLECTION_NAME = "day20_langchain"


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


def build_langchain_retriever(chunks):

    print("Loading LangChain embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    print("Creating LangChain Chroma vector store...")

    vector_store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings
    )

    ids = [
        f"{chunk['source']}_{chunk['chunk_id']}"
        for chunk in chunks
    ]

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    metadatas = [
        {
            "source": chunk["source"],
            "chunk_id": chunk["chunk_id"]
        }
        for chunk in chunks
    ]

    vector_store.add_texts(
        texts=texts,
        metadatas=metadatas,
        ids=ids
    )

    print(f"Added {len(chunks)} chunks to LangChain Chroma.")

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": TOP_K
        }
    )

    return retriever


def retrieve(query, retriever):

    start_time = time.perf_counter()

    documents = retriever.invoke(query)

    elapsed = time.perf_counter() - start_time

    results = []

    for rank, document in enumerate(documents, start=1):

        results.append({
            "rank": rank,
            "source": document.metadata.get("source"),
            "chunk_id": document.metadata.get("chunk_id"),
            "text": document.page_content
        })

    return results, elapsed