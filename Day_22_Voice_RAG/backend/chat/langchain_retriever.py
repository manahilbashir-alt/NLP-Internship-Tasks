import json
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer

from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document

from pydantic import PrivateAttr


# ------------------------------------------------------------------------
# PATHS
# ------------------------------------------------------------------------

BACKEND_ROOT = Path(
    __file__
).resolve().parent.parent

FAISS_DIR = (
    BACKEND_ROOT /
    "vectorstores" /
    "FAISS_db"
)

INDEX_PATH = (
    FAISS_DIR /
    "index.faiss"
)

METADATA_PATH = (
    FAISS_DIR /
    "metadata.json"
)


# ------------------------------------------------------------------------
# EMBEDDING MODEL
# ------------------------------------------------------------------------

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Shared model.
# It stays None during server startup.
# BGE is loaded only when retrieval/ingestion needs it.
embedding_model = None


def get_embedding_model():
    """
    Load BGE only when it is actually needed.

    The same model instance is reused by the whole backend.
    """

    global embedding_model

    if embedding_model is None:

        print(
            f"[langchain_retriever] "
            f"Loading embedding model "
            f"({EMBEDDING_MODEL})..."
        )

        embedding_model = SentenceTransformer(
            EMBEDDING_MODEL
        )

        print(
            "[langchain_retriever] "
            "Embedding model loaded."
        )

    return embedding_model


# ------------------------------------------------------------------------
# FAISS RETRIEVER
# ------------------------------------------------------------------------

class FAISSRetriever(BaseRetriever):

    k: int = 3

    _model: object = PrivateAttr(
        default=None
    )

    _index: object = PrivateAttr(
        default=None
    )

    _row_metadata: list = PrivateAttr(
        default_factory=list
    )

    def __init__(
        self,
        k=3,
        **kwargs
    ):

        super().__init__(
            k=k,
            **kwargs
        )

        print(
            "[langchain_retriever] "
            "Loading FAISS index..."
        )

        if not INDEX_PATH.exists():

            raise FileNotFoundError(
                f"FAISS index not found: "
                f"{INDEX_PATH}"
            )

        if not METADATA_PATH.exists():

            raise FileNotFoundError(
                f"FAISS metadata not found: "
                f"{METADATA_PATH}"
            )

        self._index = faiss.read_index(
            str(INDEX_PATH)
        )

        self._row_metadata = json.loads(
            METADATA_PATH.read_text(
                encoding="utf-8"
            )
        )

        print(
            f"[langchain_retriever] "
            f"FAISS index loaded: "
            f"{self._index.ntotal} vectors"
        )

    # --------------------------------------------------------------------
    # MODEL
    # --------------------------------------------------------------------

    def _get_model(self):

        self._model = get_embedding_model()

        return self._model

    # --------------------------------------------------------------------
    # LANGCHAIN RETRIEVAL
    # --------------------------------------------------------------------

    def _get_relevant_documents(
        self,
        query: str
    ) -> list[Document]:

        model = self._get_model()

        query_vector = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")

        scores, row_indices = (
            self._index.search(
                query_vector,
                self.k
            )
        )

        docs = []

        for row_idx, score in zip(
            row_indices[0],
            scores[0]
        ):

            if row_idx == -1:
                continue

            if row_idx >= len(
                self._row_metadata
            ):
                continue

            meta = self._row_metadata[
                row_idx
            ]

            docs.append(
                Document(
                    page_content=meta.get(
                        "content",
                        ""
                    ),
                    metadata={
                        "chunk_id": meta.get(
                            "chunk_id"
                        ),
                        "source_file": meta.get(
                            "source_file"
                        ),
                        "page_no": meta.get(
                            "page_no"
                        ),
                        "section": meta.get(
                            "section"
                        ),
                        "chunk_type": meta.get(
                            "chunk_type"
                        ),
                        "score": float(score),
                    }
                )
            )

        return docs

    # --------------------------------------------------------------------
    # RAW SEARCH
    # --------------------------------------------------------------------

    def search_raw(
        self,
        query: str,
        k=10
    ) -> list:

        model = self._get_model()

        query_vector = model.encode(
            [query],
            normalize_embeddings=True,
            convert_to_numpy=True
        ).astype("float32")

        scores, row_indices = (
            self._index.search(
                query_vector,
                k
            )
        )

        results = []

        for row_idx, score in zip(
            row_indices[0],
            scores[0]
        ):

            if row_idx == -1:
                continue

            if row_idx >= len(
                self._row_metadata
            ):
                continue

            meta = self._row_metadata[
                row_idx
            ]

            results.append({
                "chunk_id": meta.get(
                    "chunk_id"
                ),
                "content": meta.get(
                    "content",
                    ""
                ),
                "score": float(score),
                "page_no": meta.get(
                    "page_no"
                ),
                "section": meta.get(
                    "section"
                ),
                "source_file": meta.get(
                    "source_file"
                ),
                "chunk_type": meta.get(
                    "chunk_type"
                ),
            })

        return results

    # --------------------------------------------------------------------
    # RELOAD INDEX
    # --------------------------------------------------------------------

    def reload(self):

        self._index = faiss.read_index(
            str(INDEX_PATH)
        )

        self._row_metadata = json.loads(
            METADATA_PATH.read_text(
                encoding="utf-8"
            )
        )

        print(
            f"[langchain_retriever] "
            f"Reloaded FAISS index: "
            f"{self._index.ntotal} vectors"
        )


# ------------------------------------------------------------------------
# FACTORY
# ------------------------------------------------------------------------

def get_langchain_retriever(k=3):

    return FAISSRetriever(
        k=k
    )


# ------------------------------------------------------------------------
# TEST
# ------------------------------------------------------------------------

if __name__ == "__main__":

    retriever = get_langchain_retriever(
        k=6
    )

    query = (
        "explain support vector machines"
    )

    results = retriever.invoke(
        query
    )

    print(
        f'\nQuery: "{query}"\n'
    )

    for rank, doc in enumerate(
        results,
        start=1
    ):

        print(
            f"#{rank} "
            f"score="
            f"{doc.metadata['score']:.4f} "
            f"["
            f"{doc.metadata['source_file']}, "
            f"page "
            f"{doc.metadata['page_no']}"
            f"]"
        )

        print(
            f'     "{doc.page_content[:100]}..."\n'
        )
