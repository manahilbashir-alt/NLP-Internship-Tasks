from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import EmbeddingsFilter


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DAY17_DIR = BASE_DIR.parent / "Day17_Vector_Database_Benchmark"

CHROMA_DIR = DAY17_DIR / "data" / "chroma"


# ============================================================
# CONFIGURATION
# ============================================================

COLLECTION_NAME = "document_chunks"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

ENV_FILE = (
    BASE_DIR.parent
    / "Day_18_RAG_Retrieval_Generation"
    / ".env"
)


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(ENV_FILE)


# ============================================================
# EMBEDDINGS
# ============================================================

def create_embeddings():

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={
            "normalize_embeddings": True
        }
    )


# ============================================================
# CHROMA VECTOR STORE
# ============================================================

def create_vectorstore():

    embeddings = create_embeddings()

    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=str(CHROMA_DIR),
        embedding_function=embeddings,
        create_collection_if_not_exists=False
    )

    return vectorstore


# ============================================================
# BASIC LANGCHAIN RETRIEVER
# ============================================================

def create_retriever(top_k=4):

    vectorstore = create_vectorstore()

    retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": top_k
        }
    )

    return retriever


# ============================================================
# CONTEXTUAL COMPRESSION RETRIEVER
# ============================================================

def create_compression_retriever(top_k=4):

    base_retriever = create_retriever(
        top_k=top_k
    )

    embeddings = create_embeddings()

    compressor = EmbeddingsFilter(
        embeddings=embeddings,
        similarity_threshold=0.3,
        k=3
    )

    compression_retriever = ContextualCompressionRetriever(
        base_retriever=base_retriever,
        base_compressor=compressor
    )

    return compression_retriever


# ============================================================
# PRINT DOCUMENT
# ============================================================

def print_document(document, index):

    print("\n" + "-" * 60)

    print(f"Result {index}")

    print(
        "Source:",
        document.metadata.get(
            "source_filename",
            "Unknown"
        )
    )

    print(
        "Page:",
        document.metadata.get(
            "page_number",
            "Unknown"
        )
    )

    print(
        "Chunk:",
        document.metadata.get(
            "chunk_index",
            "Unknown"
        )
    )

    print("\nContent:")

    print(
        document.page_content[:500]
    )


# ============================================================
# TEST VECTORSTORE
# ============================================================

def test_vectorstore():

    print("=" * 70)
    print("LANGCHAIN CHROMA VECTORSTORE TEST")
    print("=" * 70)

    vectorstore = create_vectorstore()

    collection = vectorstore._collection

    print("\nChroma path:")
    print(CHROMA_DIR)

    print("\nCollection:")
    print(COLLECTION_NAME)

    print("\nDocuments in collection:")
    print(collection.count())

    query = "Who is Mr. Bingley?"

    print("\nQuery:")
    print(query)

    documents = vectorstore.similarity_search(
        query,
        k=3
    )

    print(
        "\nSimilarity search results:",
        len(documents)
    )

    for index, document in enumerate(
        documents,
        start=1
    ):

        print_document(
            document,
            index
        )


# ============================================================
# TEST BASIC RETRIEVER
# ============================================================

def test_retriever():

    print("\n\n")
    print("=" * 70)
    print("LANGCHAIN CHROMA RETRIEVER TEST")
    print("=" * 70)

    query = "Who is Mr. Bingley?"

    print("\nQuery:")
    print(query)

    retriever = create_retriever(
        top_k=3
    )

    documents = retriever.invoke(
        query
    )

    print(
        "\nRetrieved documents:",
        len(documents)
    )

    for index, document in enumerate(
        documents,
        start=1
    ):

        print_document(
            document,
            index
        )


# ============================================================
# TEST CONTEXTUAL COMPRESSION
# ============================================================

def test_compression():

    print("\n\n")
    print("=" * 70)
    print("CONTEXTUAL COMPRESSION TEST")
    print("=" * 70)

    query = "Who is Mr. Bingley?"

    print("\nQuery:")
    print(query)

    retriever = create_compression_retriever(
        top_k=4
    )

    documents = retriever.invoke(
        query
    )

    print(
        "\nCompressed documents:",
        len(documents)
    )

    for index, document in enumerate(
        documents,
        start=1
    ):

        print_document(
            document,
            index
        )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    test_vectorstore()

    test_retriever()

    test_compression()