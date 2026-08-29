from pathlib import Path
from typing import List, Sequence

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors.base import (
    BaseDocumentCompressor,
)
from langchain_core.callbacks import CallbackManagerForRetrieverRun


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = (
    Path(__file__).resolve().parent.parent / "data"
)

COLLECTION_NAME = "day20_compression"

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

TOP_K = 3


# ============================================================
# CUSTOM DOCUMENT COMPRESSOR
# ============================================================

class KeywordDocumentCompressor(
    BaseDocumentCompressor
):
    """
    Deterministic document compressor.

    It keeps only sentences that contain words
    related to the user's query.

    This allows us to demonstrate contextual
    compression without depending on an external
    LLM API.
    """

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: CallbackManagerForRetrieverRun = None,
    ) -> Sequence[Document]:

        # ----------------------------------------------------
        # Extract query words
        # ----------------------------------------------------

        query_words = {
            word.lower().strip(
                ".,?!:;()[]{}"
            )
            for word in query.split()
            if len(word) > 2
        }

        compressed_documents = []

        # ----------------------------------------------------
        # Process every retrieved document
        # ----------------------------------------------------

        for document in documents:

            text = document.page_content

            # Split document into sentences
            sentences = [
                sentence.strip()
                for sentence in text.split(".")
                if sentence.strip()
            ]

            relevant_sentences = []

            # ------------------------------------------------
            # Check sentence relevance
            # ------------------------------------------------

            for sentence in sentences:

                sentence_words = {
                    word.lower().strip(
                        ".,?!:;()[]{}"
                    )
                    for word in sentence.split()
                }

                overlap = (
                    query_words
                    & sentence_words
                )

                if overlap:
                    relevant_sentences.append(
                        sentence
                    )

            # ------------------------------------------------
            # Create compressed document
            # ------------------------------------------------

            if relevant_sentences:

                compressed_text = ". ".join(
                    relevant_sentences
                )

                compressed_documents.append(
                    Document(
                        page_content=compressed_text,
                        metadata=document.metadata.copy(),
                    )
                )

        return compressed_documents


# ============================================================
# COMPRESSION RAG
# ============================================================

class CompressionRAG:

    def __init__(self):

        print(
            "Loading embedding model..."
        )

        # ----------------------------------------------------
        # Embeddings
        # ----------------------------------------------------

        self.embeddings = (
            HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL
            )
        )

        # ----------------------------------------------------
        # Load documents
        # ----------------------------------------------------

        documents = self.load_documents()

        print(
            f"Loaded {len(documents)} documents."
        )

        # ----------------------------------------------------
        # Create chunks
        # ----------------------------------------------------

        chunks = self.create_chunks(
            documents
        )

        print(
            f"Created {len(chunks)} chunks."
        )

        # ----------------------------------------------------
        # Create Chroma
        # ----------------------------------------------------

        print(
            "Creating Chroma vector store..."
        )

        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
        )

        # ----------------------------------------------------
        # Remove previous test data
        # ----------------------------------------------------

        existing = self.vector_store.get()

        if existing["ids"]:

            self.vector_store.delete(
                ids=existing["ids"]
            )

        # ----------------------------------------------------
        # Add documents
        # ----------------------------------------------------

        ids = []

        for document in chunks:

            source = document.metadata[
                "source"
            ]

            chunk_id = document.metadata[
                "chunk_id"
            ]

            ids.append(
                f"{source}_{chunk_id}"
            )

        self.vector_store.add_documents(
            documents=chunks,
            ids=ids,
        )

        print(
            f"Added {len(chunks)} chunks."
        )

        # ====================================================
        # BASE RETRIEVER
        # ====================================================

        print(
            "Creating base Chroma retriever..."
        )

        self.base_retriever = (
            self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": TOP_K
                },
            )
        )

        # ====================================================
        # COMPRESSOR
        # ====================================================

        print(
            "Creating contextual compressor..."
        )

        self.compressor = (
            KeywordDocumentCompressor()
        )

        # ====================================================
        # CONTEXTUAL COMPRESSION RETRIEVER
        # ====================================================

        print(
            "Creating Contextual "
            "Compression Retriever..."
        )

        self.compression_retriever = (
            ContextualCompressionRetriever(
                base_compressor=self.compressor,
                base_retriever=self.base_retriever,
            )
        )

        print(
            "Contextual Compression Retriever ready."
        )

    # ========================================================
    # LOAD DOCUMENTS
    # ========================================================

    def load_documents(self):

        documents = []

        for file_path in DATA_DIR.glob(
            "*.txt"
        ):

            text = file_path.read_text(
                encoding="utf-8"
            )

            documents.append(
                {
                    "source": file_path.name,
                    "text": text,
                }
            )

        return documents

    # ========================================================
    # CREATE CHUNKS
    # ========================================================

    def create_chunks(
        self,
        documents
    ):

        chunks = []

        for document in documents:

            paragraphs = [
                paragraph.strip()
                for paragraph
                in document["text"].split(
                    "\n\n"
                )
                if paragraph.strip()
            ]

            for chunk_id, paragraph in enumerate(
                paragraphs
            ):

                chunks.append(
                    Document(
                        page_content=paragraph,
                        metadata={
                            "source":
                                document["source"],
                            "chunk_id":
                                chunk_id,
                        },
                    )
                )

        return chunks

    # ========================================================
    # NORMALIZE DOCUMENT RESULTS
    # ========================================================

    def normalize_documents(
        self,
        items
    ):

        """
        Converts returned retrieval items into
        standard LangChain Document objects.

        Some versions/configurations may return
        tuples such as:

            (Document, score)

        while normal retrievers return:

            Document
        """

        normalized = []

        for item in items:

            if isinstance(
                item,
                Document
            ):

                normalized.append(
                    item
                )

            elif isinstance(
                item,
                tuple
            ):

                # First element should be Document
                if (
                    len(item) > 0
                    and isinstance(
                        item[0],
                        Document
                    )
                ):

                    normalized.append(
                        item[0]
                    )

            else:

                # Last-resort support for objects
                # containing a document
                if hasattr(
                    item,
                    "page_content"
                ):

                    normalized.append(
                        item
                    )

        return normalized

    # ========================================================
    # ORIGINAL RETRIEVAL
    # ========================================================

    def retrieve_original(
        self,
        query
    ):

        documents = (
            self.base_retriever.invoke(
                query
            )
        )

        return self.normalize_documents(
            documents
        )

    # ========================================================
    # COMPRESSED RETRIEVAL
    # ========================================================

    def retrieve_compressed(
        self,
        query
    ):

        documents = (
            self.compression_retriever.invoke(
                query
            )
        )

        return self.normalize_documents(
            documents
        )

    # ========================================================
    # COMPLETE RETRIEVAL
    # ========================================================

    def compare_retrieval(
        self,
        query
    ):

        original = (
            self.retrieve_original(
                query
            )
        )

        compressed = (
            self.retrieve_compressed(
                query
            )
        )

        return original, compressed