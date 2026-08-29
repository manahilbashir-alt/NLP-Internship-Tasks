from pathlib import Path
from typing import Dict, List

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document


# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = (
    Path(__file__).resolve().parent.parent / "data"
)

COLLECTION_NAME = "day20_conversational_rag"

EMBEDDING_MODEL = (
    "sentence-transformers/all-MiniLM-L6-v2"
)

TOP_K = 3


# ============================================================
# CONVERSATIONAL RAG
# ============================================================

class ConversationalRAG:

    def __init__(self):

        print("Loading embedding model...")

        # ----------------------------------------------------
        # Embedding model
        # ----------------------------------------------------

        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL
        )

        # ----------------------------------------------------
        # Session memory
        #
        # Structure:
        #
        # {
        #     "session_1": [
        #         {"role": "user", "content": "..."},
        #         {"role": "assistant", "content": "..."}
        #     ]
        # }
        # ----------------------------------------------------

        self.sessions: Dict[
            str,
            List[Dict[str, str]]
        ] = {}

        # ----------------------------------------------------
        # Load documents
        # ----------------------------------------------------

        print("Loading documents...")

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
        # Create Chroma vector store
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

            filename = document.metadata[
                "filename"
            ]

            page = document.metadata[
                "page"
            ]

            chunk_id = document.metadata[
                "chunk_id"
            ]

            ids.append(
                f"{filename}_"
                f"page_{page}_"
                f"chunk_{chunk_id}"
            )

        self.vector_store.add_documents(
            documents=chunks,
            ids=ids,
        )

        print(
            f"Added {len(chunks)} chunks to Chroma."
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
    # CREATE CHUNKS
    # ========================================================

    def create_chunks(
        self,
        documents
    ):

        chunks = []

        for document in documents:

            filename = document["source"]

            # ------------------------------------------------
            # TXT files do not have physical PDF pages.
            #
            # Therefore each TXT document is treated as
            # logical Page 1.
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
                            "source": filename,
                            "filename": filename,
                            "page": page_number,
                            "chunk_id": chunk_id,
                        },
                    )
                )

        return chunks

    # ========================================================
    # SESSION MANAGEMENT
    # ========================================================

    def create_session(
        self,
        session_id: str
    ):

        if session_id not in self.sessions:

            self.sessions[
                session_id
            ] = []

    # ========================================================
    # GET SESSION HISTORY
    # ========================================================

    def get_history(
        self,
        session_id: str
    ):

        return self.sessions.get(
            session_id,
            []
        )

    # ========================================================
    # SAVE MESSAGE
    # ========================================================

    def save_message(
        self,
        session_id: str,
        role: str,
        content: str
    ):

        self.create_session(
            session_id
        )

        self.sessions[
            session_id
        ].append(
            {
                "role": role,
                "content": content,
            }
        )

    # ========================================================
    # CONVERT HISTORY TO TEXT
    # ========================================================

    def history_to_text(
        self,
        session_id: str
    ):

        history = self.get_history(
            session_id
        )

        if not history:

            return ""

        lines = []

        for message in history:

            role = message["role"]

            content = message["content"]

            if role == "user":

                lines.append(
                    f"User: {content}"
                )

            else:

                lines.append(
                    f"Assistant: {content}"
                )

        return "\n".join(lines)

    # ========================================================
    # CONTEXTUALIZE QUESTION
    # ========================================================

    def contextualize_question(
        self,
        session_id: str,
        question: str
    ):

        history = self.get_history(
            session_id
        )

        # ----------------------------------------------------
        # First question needs no contextualization
        # ----------------------------------------------------

        if not history:

            return question

        # ----------------------------------------------------
        # Find previous user question
        # ----------------------------------------------------

        previous_question = None

        for message in reversed(history):

            if (
                message["role"]
                == "user"
            ):

                previous_question = (
                    message["content"]
                )

                break

        if not previous_question:

            return question

        # ----------------------------------------------------
        # Simple follow-up detection
        # ----------------------------------------------------

        follow_up_phrases = [
            "what about",
            "what about the",
            "and the",
            "what is the second",
            "what is the first",
            "what is the third",
            "tell me more",
            "explain more",
            "why",
            "how about",
            "can you explain",
        ]

        question_lower = (
            question.lower().strip()
        )

        is_follow_up = any(
            phrase in question_lower
            for phrase
            in follow_up_phrases
        )

        # ----------------------------------------------------
        # Pronoun/reference detection
        # ----------------------------------------------------

        reference_words = [
            "it",
            "they",
            "them",
            "this",
            "that",
            "these",
            "those",
            "second",
            "first",
            "third",
            "previous",
        ]

        contains_reference = any(
            word in question_lower.split()
            for word in reference_words
        )

        # ----------------------------------------------------
        # Contextualize
        # ----------------------------------------------------

        if (
            is_follow_up
            or contains_reference
        ):

            return (
                "Regarding the previous "
                f"question '{previous_question}', "
                f"the user now asks: {question}"
            )

        # ----------------------------------------------------
        # Independent question
        # ----------------------------------------------------

        return question

    # ========================================================
    # RETRIEVE DOCUMENTS
    # ========================================================

    def retrieve(
        self,
        query: str
    ):

        documents = (
            self.retriever.invoke(
                query
            )
        )

        return documents

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    def build_context(
        self,
        documents
    ):

        context_parts = []

        for document in documents:

            filename = document.metadata.get(
                "filename",
                document.metadata.get(
                    "source",
                    "unknown"
                )
            )

            page = document.metadata.get(
                "page",
                1
            )

            chunk_id = document.metadata.get(
                "chunk_id",
                "unknown"
            )

            context_parts.append(
                f"[Source: {filename}, "
                f"Page: {page}, "
                f"Chunk: {chunk_id}]\n"
                f"{document.page_content}"
            )

        return "\n\n".join(
            context_parts
        )

    # ========================================================
    # GENERATE GROUNDED ANSWER
    # ========================================================

    def generate_answer(
        self,
        question: str,
        documents
    ):

        if not documents:

            return (
                "I could not find relevant "
                "information in the provided "
                "documents."
            )

        # ----------------------------------------------------
        # For the current Day 20 implementation,
        # answer directly from retrieved context.
        # ----------------------------------------------------

        answer_parts = []

        for document in documents:

            filename = document.metadata.get(
                "filename",
                document.metadata.get(
                    "source",
                    "unknown"
                )
            )

            page = document.metadata.get(
                "page",
                1
            )

            answer_parts.append(
                document.page_content
            )

        answer = " ".join(
            answer_parts
        )

        return answer

    # ========================================================
    # EXTRACT SOURCES
    # ========================================================

    def extract_sources(
        self,
        documents
    ):

        sources = []

        for document in documents:

            filename = document.metadata.get(
                "filename",
                document.metadata.get(
                    "source",
                    "unknown"
                )
            )

            page = document.metadata.get(
                "page",
                1
            )

            source = {
                "filename": filename,
                "page": page,
            }

            if source not in sources:

                sources.append(
                    source
                )

        return sources

    # ========================================================
    # COMPLETE CHAT
    # ========================================================

    def chat(
        self,
        session_id: str,
        question: str
    ):

        # ----------------------------------------------------
        # Create session if necessary
        # ----------------------------------------------------

        self.create_session(
            session_id
        )

        # ----------------------------------------------------
        # Contextualize question using history
        # ----------------------------------------------------

        contextualized_question = (
            self.contextualize_question(
                session_id,
                question
            )
        )

        # ----------------------------------------------------
        # Retrieve relevant documents
        # ----------------------------------------------------

        documents = self.retrieve(
            contextualized_question
        )

        # ----------------------------------------------------
        # Build grounded answer
        # ----------------------------------------------------

        answer = self.generate_answer(
            contextualized_question,
            documents
        )

        # ----------------------------------------------------
        # Extract source citations
        # ----------------------------------------------------

        sources = self.extract_sources(
            documents
        )

        # ----------------------------------------------------
        # Save USER message
        # ----------------------------------------------------

        self.save_message(
            session_id=session_id,
            role="user",
            content=question,
        )

        # ----------------------------------------------------
        # Save ASSISTANT message
        # ----------------------------------------------------

        self.save_message(
            session_id=session_id,
            role="assistant",
            content=answer,
        )

        # ----------------------------------------------------
        # Return complete result
        # ----------------------------------------------------

        return {
            "session_id": session_id,
            "question": question,
            "contextualized_question":
                contextualized_question,
            "answer": answer,
            "sources": sources,
            "history_length": len(
                self.get_history(
                    session_id
                )
            ),
            "retrieved_documents":
                documents,
        }


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 80)
    print(
        "DAY 20 - CONVERSATIONAL RAG MANUAL TEST"
    )
    print("=" * 80)

    rag = ConversationalRAG()

    session_id = "test_session"

    # --------------------------------------------------------
    # Turn 1
    # --------------------------------------------------------

    result1 = rag.chat(
        session_id=session_id,
        question="What is ChromaDB?"
    )

    print("\nTURN 1")
    print("-" * 80)

    print(
        "Question:",
        result1["question"]
    )

    print(
        "Contextualized:",
        result1[
            "contextualized_question"
        ]
    )

    print(
        "Answer:",
        result1["answer"]
    )

    print(
        "Sources:",
        result1["sources"]
    )

    print(
        "History:",
        result1["history_length"]
    )

    # --------------------------------------------------------
    # Turn 2
    # --------------------------------------------------------

    result2 = rag.chat(
        session_id=session_id,
        question="What about the second point?"
    )

    print("\nTURN 2")
    print("-" * 80)

    print(
        "Question:",
        result2["question"]
    )

    print(
        "Contextualized:",
        result2[
            "contextualized_question"
        ]
    )

    print(
        "Answer:",
        result2["answer"]
    )

    print(
        "Sources:",
        result2["sources"]
    )

    print(
        "History:",
        result2["history_length"]
    )

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print(
        "CONVERSATIONAL RAG TEST COMPLETE"
    )
    print("=" * 80)