"""
================================================================================
 DAY 17 - STEP 5: FAISS SETUP
================================================================================

WHAT THIS FILE DOES:
  - Loads saved embeddings
  - Builds a FAISS index
  - Stores chunk metadata separately
  - Searches the FAISS index
  - Adds newly ingested document chunks

IMPORTANT:
  The BGE embedding model is shared with
  chat.langchain_retriever.

  The model is loaded LAZILY, only when embedding is actually needed.
  This avoids loading multiple copies of BGE-large and helps prevent
  Windows paging-file / memory errors.
================================================================================
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np
import faiss


# ------------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

CHUNKS_PATH = PROJECT_ROOT / "chunking" / "chunks.json"

EMBEDDINGS_DIR = PROJECT_ROOT / "embeddings"

FAISS_DIR = PROJECT_ROOT / "vectorstores" / "FAISS_db"

INDEX_PATH = FAISS_DIR / "index.faiss"

METADATA_PATH = FAISS_DIR / "metadata.json"

DEFAULT_MODEL = "all-MiniLM-L6-v2"


# ------------------------------------------------------------------------
# MODEL MAPPING
# ------------------------------------------------------------------------

MODEL_ID_MAP = {
    "all-MiniLM-L6-v2":
        "sentence-transformers/all-MiniLM-L6-v2",

    "all-mpnet-base-v2":
        "sentence-transformers/all-mpnet-base-v2",

    "bge-large-en-v1.5":
        "BAAI/bge-large-en-v1.5",
}


# ------------------------------------------------------------------------
# EMBEDDING MODEL
# ------------------------------------------------------------------------

def get_model(model_name=DEFAULT_MODEL):
    """
    Returns the embedding model.

    For BGE-large, reuse the shared lazy-loaded model from
    chat.langchain_retriever.

    This prevents loading another BGE-large copy into memory.
    """

    if model_name == DEFAULT_MODEL:

        from chat.langchain_retriever import get_embedding_model

        return get_embedding_model()

    from sentence_transformers import SentenceTransformer

    model_id = MODEL_ID_MAP.get(
        model_name,
        model_name
    )

    print(
        f"[faiss_manager] Loading embedding model: "
        f"{model_id}"
    )

    model = SentenceTransformer(model_id)

    print(
        "[faiss_manager] Embedding model loaded."
    )

    return model


# ------------------------------------------------------------------------
# LOAD CHUNKS
# ------------------------------------------------------------------------

def load_chunks() -> dict:
    """
    Loads chunks.json and returns:

        {
            chunk_id: chunk_dict
        }
    """

    if not CHUNKS_PATH.exists():

        raise FileNotFoundError(
            f"{CHUNKS_PATH} not found. "
            f"Run the chunker first."
        )

    data = json.loads(
        CHUNKS_PATH.read_text(
            encoding="utf-8"
        )
    )

    return {
        c["chunk_id"]: c
        for c in data
    }


# ------------------------------------------------------------------------
# LOAD SAVED EMBEDDINGS
# ------------------------------------------------------------------------

def load_embeddings(model_name: str):
    """
    Loads:

        embeddings.npy
        chunk_ids.json

    Returns:

        chunk_ids
        embeddings
    """

    model_dir = (
        EMBEDDINGS_DIR /
        model_name
    )

    embeddings_path = (
        model_dir /
        "embeddings.npy"
    )

    ids_path = (
        model_dir /
        "chunk_ids.json"
    )

    if (
        not embeddings_path.exists()
        or
        not ids_path.exists()
    ):

        raise FileNotFoundError(
            f"No saved embeddings found for "
            f"'{model_name}' in {model_dir}. "
            f"Run the embedding step first."
        )

    embeddings = np.load(
        embeddings_path
    ).astype("float32")

    chunk_ids = json.loads(
        ids_path.read_text(
            encoding="utf-8"
        )
    )

    return (
        chunk_ids,
        embeddings
    )


# ------------------------------------------------------------------------
# CORE ACTION 1: BUILD
# ------------------------------------------------------------------------

def build(model_name=DEFAULT_MODEL):

    chunks_by_id = load_chunks()

    chunk_ids, embeddings = (
        load_embeddings(model_name)
    )

    dimension = embeddings.shape[1]

    print(
        f"[build] {len(chunk_ids)} vectors, "
        f"dimension={dimension}"
    )

    # ------------------------------------------------------------
    # Inner Product on normalized vectors
    # = cosine similarity
    # ------------------------------------------------------------

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    # ------------------------------------------------------------
    # Metadata mapping
    # ------------------------------------------------------------

    row_metadata = []

    for chunk_id in chunk_ids:

        chunk = chunks_by_id.get(
            chunk_id,
            {}
        )

        row_metadata.append({

            "chunk_id":
                chunk_id,

            "content":
                chunk.get(
                    "content",
                    ""
                ),

            "page_no":
                chunk.get(
                    "page_no"
                ),

            "section":
                chunk.get(
                    "section"
                ),

            "chunk_type":
                chunk.get(
                    "chunk_type"
                ),

            "source_file":
                chunk.get(
                    "source_file"
                ),

            "prev_chunk_id":
                chunk.get(
                    "prev_chunk_id"
                ),

            "next_chunk_id":
                chunk.get(
                    "next_chunk_id"
                ),
        })

    # ------------------------------------------------------------
    # Create directory
    # ------------------------------------------------------------

    FAISS_DIR.mkdir(
        exist_ok=True,
        parents=True
    )

    # ------------------------------------------------------------
    # Save FAISS index
    # ------------------------------------------------------------

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    # ------------------------------------------------------------
    # Save metadata
    # ------------------------------------------------------------

    METADATA_PATH.write_text(
        json.dumps(
            row_metadata,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"[build] FAISS index saved to "
        f"{INDEX_PATH}"
    )

    print(
        f"[build] Metadata for "
        f"{len(row_metadata)} rows "
        f"saved to {METADATA_PATH}"
    )


# ------------------------------------------------------------------------
# CORE ACTION 2: COUNT
# ------------------------------------------------------------------------

def count_chunks():

    if not INDEX_PATH.exists():

        print(
            "[count] FAISS index does not exist."
        )

        return 0

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    print(
        f"[count] FAISS index has "
        f"{index.ntotal} vectors."
    )

    return index.ntotal


# ------------------------------------------------------------------------
# CORE ACTION 3: SEARCH
# ------------------------------------------------------------------------

def search(
    query: str,
    k=3,
    model_name=DEFAULT_MODEL
):
    """
    Search FAISS using a text query.
    """

    # ------------------------------------------------------------
    # Load shared embedding model
    # ------------------------------------------------------------

    model = get_model(
        model_name
    )

    # ------------------------------------------------------------
    # Check FAISS index
    # ------------------------------------------------------------

    if not INDEX_PATH.exists():

        raise FileNotFoundError(
            f"FAISS index not found at "
            f"{INDEX_PATH}"
        )

    if not METADATA_PATH.exists():

        raise FileNotFoundError(
            f"FAISS metadata not found at "
            f"{METADATA_PATH}"
        )

    # ------------------------------------------------------------
    # Load index + metadata
    # ------------------------------------------------------------

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    row_metadata = json.loads(
        METADATA_PATH.read_text(
            encoding="utf-8"
        )
    )

    # ------------------------------------------------------------
    # Encode query
    # ------------------------------------------------------------

    query_vector = model.encode(
        [query],
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype("float32")

    # ------------------------------------------------------------
    # FAISS search
    # ------------------------------------------------------------

    start = time.time()

    scores, row_indices = (
        index.search(
            query_vector,
            k
        )
    )

    elapsed_ms = (
        time.time() - start
    ) * 1000

    print(
        f'[search] Query: "{query}" '
        f"(search took {elapsed_ms:.2f} ms)"
    )

    # ------------------------------------------------------------
    # Display results
    # ------------------------------------------------------------

    results = []

    for rank, (
        row_idx,
        score
    ) in enumerate(
        zip(
            row_indices[0],
            scores[0]
        ),
        start=1
    ):

        if row_idx < 0:
            continue

        if row_idx >= len(
            row_metadata
        ):
            continue

        meta = row_metadata[
            row_idx
        ]

        preview = (
            meta.get(
                "content",
                ""
            )[:80]
            .replace(
                "\n",
                " "
            )
        )

        print(
            f"  #{rank} "
            f"score={score:.4f} "
            f"{meta.get('chunk_id')} "
            f"[{meta.get('chunk_type')}, "
            f"page {meta.get('page_no')}, "
            f"section: "
            f"{meta.get('section')}]"
        )

        print(
            f'        "{preview}..."'
        )

        results.append({
            "chunk_id":
                meta.get(
                    "chunk_id"
                ),

            "content":
                meta.get(
                    "content",
                    ""
                ),

            "score":
                float(score),

            "page_no":
                meta.get(
                    "page_no"
                ),

            "section":
                meta.get(
                    "section"
                ),

            "chunk_type":
                meta.get(
                    "chunk_type"
                ),

            "source_file":
                meta.get(
                    "source_file"
                ),
        })

    return results


# ------------------------------------------------------------------------
# CORE ACTION 4: ADD DOCUMENT
# ------------------------------------------------------------------------

def add_document(
    new_chunks: list,
    model_name=DEFAULT_MODEL
):
    """
    Embeds and appends new chunks to the existing FAISS index.

    IMPORTANT:
      BGE-large uses the shared lazy-loaded model from
      chat.langchain_retriever.

    This prevents multiple copies of the large model from
    being loaded into RAM.
    """

    if not new_chunks:

        print(
            "[add] No new chunks to add."
        )

        return count_chunks()

    print(
        f"[add] Preparing to embed "
        f"{len(new_chunks)} new chunks..."
    )

    # ------------------------------------------------------------
    # 1. GET EMBEDDING MODEL
    # ------------------------------------------------------------

    model = get_model(
        model_name
    )

    # ------------------------------------------------------------
    # 2. EXTRACT TEXT
    # ------------------------------------------------------------

    texts = [
        c.get(
            "content",
            ""
        )
        for c in new_chunks
    ]

    # ------------------------------------------------------------
    # 3. CREATE EMBEDDINGS
    # ------------------------------------------------------------

    new_embeddings = model.encode(
        texts,
        normalize_embeddings=True,
        convert_to_numpy=True
    ).astype("float32")

    print(
        f"[add] Created embeddings: "
        f"{new_embeddings.shape}"
    )

    # ------------------------------------------------------------
    # 4. LOAD EXISTING INDEX
    # ------------------------------------------------------------

    if (
        INDEX_PATH.exists()
        and
        METADATA_PATH.exists()
    ):

        index = faiss.read_index(
            str(INDEX_PATH)
        )

        row_metadata = json.loads(
            METADATA_PATH.read_text(
                encoding="utf-8"
            )
        )

        print(
            f"[add] Existing FAISS index: "
            f"{index.ntotal} vectors"
        )

    else:

        dimension = (
            new_embeddings.shape[1]
        )

        index = faiss.IndexFlatIP(
            dimension
        )

        row_metadata = []

        print(
            "[add] No existing FAISS index. "
            "Creating a new one."
        )

    # ------------------------------------------------------------
    # 5. ADD VECTORS
    # ------------------------------------------------------------

    index.add(
        new_embeddings
    )

    # ------------------------------------------------------------
    # 6. ADD METADATA
    # ------------------------------------------------------------

    for chunk in new_chunks:

        row_metadata.append({

            "chunk_id":
                chunk.get(
                    "chunk_id"
                ),

            "content":
                chunk.get(
                    "content",
                    ""
                ),

            "page_no":
                chunk.get(
                    "page_no"
                ),

            "section":
                chunk.get(
                    "section"
                ),

            "chunk_type":
                chunk.get(
                    "chunk_type"
                ),

            "source_file":
                chunk.get(
                    "source_file"
                ),

            "prev_chunk_id":
                chunk.get(
                    "prev_chunk_id"
                ),

            "next_chunk_id":
                chunk.get(
                    "next_chunk_id"
                ),
        })

    # ------------------------------------------------------------
    # 7. SAVE INDEX + METADATA
    # ------------------------------------------------------------

    FAISS_DIR.mkdir(
        exist_ok=True,
        parents=True
    )

    faiss.write_index(
        index,
        str(INDEX_PATH)
    )

    METADATA_PATH.write_text(
        json.dumps(
            row_metadata,
            indent=2
        ),
        encoding="utf-8"
    )

    print(
        f"[add] Added "
        f"{len(new_chunks)} new chunks."
    )

    print(
        f"[add] Index now has "
        f"{index.ntotal} total vectors."
    )

    return index.ntotal


# ------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------

def main():

    parser = argparse.ArgumentParser(
        description="FAISS setup and search"
    )

    subparsers = (
        parser.add_subparsers(
            dest="command",
            required=True
        )
    )

    # ------------------------------------------------------------
    # BUILD
    # ------------------------------------------------------------

    p_build = (
        subparsers.add_parser(
            "build",
            help=(
                "Build FAISS index "
                "from saved embeddings"
            )
        )
    )

    p_build.add_argument(
        "--model",
        default=DEFAULT_MODEL
    )

    # ------------------------------------------------------------
    # COUNT
    # ------------------------------------------------------------

    subparsers.add_parser(
        "count",
        help="Show number of indexed vectors"
    )

    # ------------------------------------------------------------
    # SEARCH
    # ------------------------------------------------------------

    p_search = (
        subparsers.add_parser(
            "search",
            help="Search FAISS index"
        )
    )

    p_search.add_argument(
        "--query",
        required=True
    )

    p_search.add_argument(
        "--k",
        type=int,
        default=3
    )

    p_search.add_argument(
        "--model",
        default=DEFAULT_MODEL
    )

    # ------------------------------------------------------------
    # PARSE
    # ------------------------------------------------------------

    args = parser.parse_args()

    # ------------------------------------------------------------
    # COMMANDS
    # ------------------------------------------------------------

    if args.command == "build":

        build(
            model_name=args.model
        )

    elif args.command == "count":

        count_chunks()

    elif args.command == "search":

        search(
            args.query,
            k=args.k,
            model_name=args.model
        )


# ------------------------------------------------------------------------
# ENTRY POINT
# ------------------------------------------------------------------------

if __name__ == "__main__":

    main()
