from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = (
    Path(__file__).resolve().parent.parent / "data"
)

COLLECTION_NAME = "day20_citation_rag"

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

TOP_K = 3


# ============================================================
# CITATION RAG
# ============================================================

class CitationRAG:

    def __init__(self):

        print("Loading embedding model...")

        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

        documents = self.load_documents()

        print(
            f"Loaded {len(documents)} documents."
        )

        chunks = self.create_chunks(
            documents
        )

        print(
            f"Created {len(chunks)} chunks."
        )

        print(
            "Creating Chroma vector store..."
        )

        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embeddings,
        )

        # ----------------------------------------------------
        # Clear old test collection
        # ----------------------------------------------------

        existing = self.vector_store.get()

        if existing["ids"]:

            self.vector_store.delete(
                ids=existing["ids"]
            )

        # ----------------------------------------------------
        # Add chunks
        # ----------------------------------------------------

        ids = []

        for document in chunks:

            source = document.metadata[
                "source"
            ]

            page = document.metadata[
                "page"
            ]

            chunk_id = document.metadata[
                "chunk_id"
            ]

            ids.append(
                f"{source}_"
                f"page_{page}_"
                f"chunk_{chunk_id}"
            )

        self.vector_store.add_documents(
            documents=chunks,
            ids=ids,
        )

        print(
            f"Added {len(chunks)} chunks."
        )

        # ----------------------------------------------------
        # Retriever
        # ----------------------------------------------------

        self.retriever = (
            self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={
                    "k": TOP_K
                },
            )
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
    # CREATE CHUNKS + CITATION METADATA
    # ========================================================

    def create_chunks(
        self,
        documents
    ):

        chunks = []

        for document in documents:

            source = document["source"]

            # ------------------------------------------------
            # TXT files don't have physical PDF pages.
            #
            # We therefore treat the complete TXT document
            # as logical page 1.
            # ------------------------------------------------

            page_number = 1

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
                            "source": source,
                            "filename": source,
                            "page": page_number,
                            "chunk_id": chunk_id,
                        },
                    )
                )

        return chunks

    # ========================================================
    # RETRIEVE
    # ========================================================

    def retrieve(
        self,
        query
    ):

        documents = self.retriever.invoke(
            query
        )

        return documents

    # ========================================================
    # FORMAT CITATION
    # ========================================================

    def format_citation(
        self,
        document
    ):

        filename = document.metadata.get(
            "filename",
            document.metadata.get(
                "source",
                "unknown"
            )
        )

        page = document.metadata.get(
            "page",
            "unknown"
        )

        return (
            f"{filename} "
            f"(Page {page})"
        )

    # ========================================================
    # BUILD ANSWER
    # ========================================================

    def generate_answer(
        self,
        query,
        documents
    ):

        if not documents:

            return (
                "I could not find relevant "
                "information in the documents."
            )

        # ----------------------------------------------------
        # Use retrieved documents as grounded context
        # ----------------------------------------------------

        answer_parts = []

        for document in documents:

            citation = self.format_citation(
                document
            )

            answer_parts.append(
                f"{document.page_content}\n"
                f"Source: {citation}"
            )

        answer = "\n\n".join(
            answer_parts
        )

        return answer

    # ========================================================
    # COMPLETE RAG RESPONSE
    # ========================================================

    def chat(
        self,
        query
    ):

        documents = self.retrieve(
            query
        )

        answer = self.generate_answer(
            query,
            documents
        )

        citations = []

        for document in documents:

            citation = self.format_citation(
                document
            )

            if citation not in citations:

                citations.append(
                    citation
                )

        return {
            "question": query,
            "answer": answer,
            "sources": citations,
            "documents": documents,
        }