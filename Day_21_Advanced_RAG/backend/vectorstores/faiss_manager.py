"""
================================================================================
 DAY 17 - STEP 5: FAISS SETUP (same chunks, for speed comparison vs ChromaDB)
================================================================================
WHAT THIS FILE DOES:
  Loads the same 1218 chunks + the same all-MiniLM-L6-v2 embeddings you
  already saved in Step 3, and stores them in FAISS instead of ChromaDB.
  This lets us do a fair, apples-to-apples QUERY SPEED comparison between
  the two vector stores later, since both hold identical data.

HOW FAISS IS DIFFERENT FROM CHROMADB (plain words):
  ChromaDB is a full "vector database" - it stores vectors AND your text
  AND your metadata together, and handles saving/loading to disk for you.

  FAISS is just a very fast MATH LIBRARY for searching vectors. It ONLY
  stores the number-vectors - it has no idea what text or metadata they
  belong to. So WE have to keep a separate mapping file ourselves:
  "FAISS row 0 = chunk_0000, FAISS row 1 = chunk_0001, ..." and look up
  the text/metadata in that mapping whenever FAISS gives us a result.

  This is exactly why FAISS is usually faster for pure search - it's not
  doing any of that extra bookkeeping work ChromaDB does automatically.

WHAT WE'RE BUILDING:
  1. A FAISS "index" (the actual searchable structure of vectors)
  2. A metadata.json side-file mapping FAISS row number -> chunk info
  3. Utility functions: build, search, count (matching Chroma's utilities
     as closely as possible, so the Step 6 comparison is fair)

HOW TO RUN:
  pip install faiss-cpu --break-system-packages
  python vectorstores/faiss_manager.py build
  python vectorstores/faiss_manager.py count
  python vectorstores/faiss_manager.py search --query "what is supervised learning" --k 3

OUTPUT:
  FAISS_db/
    index.faiss       <- the actual FAISS vector index
    metadata.json       <- row_number -> {chunk_id, content, page_no, section, ...}
================================================================================
"""

import argparse
import json
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

DEFAULT_MODEL = "bge-large-en-v1.5"   # must match a model already embedded in Step 3


# ------------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------------
def load_chunks() -> dict:
    """Loads chunks.json and returns it as {chunk_id: chunk_dict}."""
    if not CHUNKS_PATH.exists():
        raise FileNotFoundError(f"{CHUNKS_PATH} not found. Run the chunker first.")
    data = json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))
    return {c["chunk_id"]: c for c in data}


def load_embeddings(model_name: str):
    """
    Loads the .npy embeddings + chunk_ids.json saved by Step 3.
    Returns (chunk_ids_in_order, embeddings_matrix) - the order here
    becomes the FAISS row order (row 0 = chunk_ids_in_order[0], etc).
    """
    model_dir = EMBEDDINGS_DIR / model_name
    embeddings_path = model_dir / "embeddings.npy"
    ids_path = model_dir / "chunk_ids.json"

    if not embeddings_path.exists() or not ids_path.exists():
        raise FileNotFoundError(
            f"No saved embeddings found for '{model_name}' in {model_dir}. "
            f"Run embeddings/embedding_benchmark.py first."
        )

    embeddings = np.load(embeddings_path).astype("float32")   # FAISS requires float32
    chunk_ids = json.loads(ids_path.read_text(encoding="utf-8"))
    return chunk_ids, embeddings


# ------------------------------------------------------------------------
# CORE ACTION 1: BUILD (create the FAISS index + metadata side-file)
# ------------------------------------------------------------------------
def build(model_name=DEFAULT_MODEL):
    chunks_by_id = load_chunks()
    chunk_ids, embeddings = load_embeddings(model_name)

    dimension = embeddings.shape[1]
    print(f"[build] {len(chunk_ids)} vectors, dimension={dimension}")

    # IndexFlatIP = exact search using inner product (dot product).
    # Since our embeddings are normalized (Step 3 used normalize_embeddings=True),
    # inner product here is equivalent to cosine similarity - same scoring
    # approach as the "hnsw:space": "cosine" setting we used for ChromaDB,
    # which keeps the comparison between the two stores fair.
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # FAISS only stores vectors, indexed by row number (0, 1, 2, ...).
    # This metadata file is how we translate "row 7" back into real chunk info.
    row_metadata = []
    for chunk_id in chunk_ids:
        chunk = chunks_by_id.get(chunk_id, {})
        row_metadata.append({
            "chunk_id": chunk_id,
            "content": chunk.get("content", ""),
            "page_no": chunk.get("page_no"),
            "section": chunk.get("section"),
            "chunk_type": chunk.get("chunk_type"),
            "source_file": chunk.get("source_file"),
            "prev_chunk_id": chunk.get("prev_chunk_id"),
            "next_chunk_id": chunk.get("next_chunk_id"),
        })

    FAISS_DIR.mkdir(exist_ok=True)
    faiss.write_index(index, str(INDEX_PATH))
    METADATA_PATH.write_text(json.dumps(row_metadata, indent=2), encoding="utf-8")

    print(f"[build] FAISS index saved to {INDEX_PATH}")
    print(f"[build] Metadata for {len(row_metadata)} rows saved to {METADATA_PATH}")

# ------------------------------------------------------------------------
# CORE ACTION 4: ADD (incrementally add new chunks, without rebuilding)
# ------------------------------------------------------------------------
def add_document(new_chunks: list, model_name=DEFAULT_MODEL):
    """
    Embeds and appends new chunks (from a freshly-ingested document) into
    the EXISTING FAISS index + metadata.json, without touching what's
    already indexed. This is what /api/rag/ingest calls per upload.

    new_chunks: list of chunk dicts, same shape as chunks.json entries
                e.g. {"chunk_id", "content", "page_no", "section",
                      "chunk_type", "source_file"}
    """
    from sentence_transformers import SentenceTransformer

    model_id_map = {
        "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
        "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
        "bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
    }
    model = SentenceTransformer(model_id_map.get(model_name, model_name))

    # 1. Embed just the new chunks
    texts = [c["content"] for c in new_chunks]
    new_embeddings = model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
    new_embeddings = new_embeddings.astype("float32")

    # 2. Load the existing index + metadata (or start fresh if none exist)
    if INDEX_PATH.exists() and METADATA_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        row_metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    else:
        dimension = new_embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        row_metadata = []

    # 3. Append new vectors — FAISS just adds them as new rows at the end
    index.add(new_embeddings)

    # 4. Append matching metadata, same order as the vectors just added
    for chunk in new_chunks:
        row_metadata.append({
            "chunk_id": chunk.get("chunk_id"),
            "content": chunk.get("content", ""),
            "page_no": chunk.get("page_no"),
            "section": chunk.get("section"),
            "chunk_type": chunk.get("chunk_type"),
            "source_file": chunk.get("source_file"),
            "prev_chunk_id": chunk.get("prev_chunk_id"),
            "next_chunk_id": chunk.get("next_chunk_id"),
        })

    # 5. Save both back to disk
    FAISS_DIR.mkdir(exist_ok=True, parents=True)
    faiss.write_index(index, str(INDEX_PATH))
    METADATA_PATH.write_text(json.dumps(row_metadata, indent=2), encoding="utf-8")

    print(f"[add] Added {len(new_chunks)} new chunks. Index now has {index.ntotal} total vectors.")
    return index.ntotal
# ------------------------------------------------------------------------
# CORE ACTION 2: COUNT
# ------------------------------------------------------------------------
def count_chunks():
    index = faiss.read_index(str(INDEX_PATH))
    print(f"[count] FAISS index has {index.ntotal} vectors.")
    return index.ntotal


# ------------------------------------------------------------------------
# CORE ACTION 3: SEARCH (embed a query live, then search the index)
# ------------------------------------------------------------------------
def search(query: str, k=3, model_name=DEFAULT_MODEL):
    from sentence_transformers import SentenceTransformer
    import time

    model_id_map = {
        "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
        "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
        "bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
    }
    model = SentenceTransformer(model_id_map.get(model_name, model_name))

    index = faiss.read_index(str(INDEX_PATH))
    row_metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    query_vector = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
    query_vector = query_vector.astype("float32")

    start = time.time()
    scores, row_indices = index.search(query_vector, k)
    elapsed_ms = (time.time() - start) * 1000

    print(f"[search] Query: \"{query}\"  (search took {elapsed_ms:.2f} ms)")
    for rank, (row_idx, score) in enumerate(zip(row_indices[0], scores[0]), start=1):
        meta = row_metadata[row_idx]
        preview = meta["content"][:80].replace("\n", " ")
        print(f"  #{rank}  score={score:.4f}  {meta['chunk_id']} "
              f"[{meta['chunk_type']}, page {meta['page_no']}, section: {meta['section']}]")
        print(f"        \"{preview}...\"")


# ------------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="FAISS setup and search")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_build = subparsers.add_parser("build", help="Build the FAISS index from saved embeddings")
    p_build.add_argument("--model", default=DEFAULT_MODEL)
    
    subparsers.add_parser("count", help="Show how many vectors are indexed")

    p_search = subparsers.add_parser("search", help="Search the index with a text query")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--k", type=int, default=3)
    p_search.add_argument("--model", default=DEFAULT_MODEL)

    args = parser.parse_args()

    if args.command == "build":
        build(model_name=args.model)
    elif args.command == "count":
        count_chunks()
    elif args.command == "search":
        search(args.query, k=args.k, model_name=args.model)
    
if __name__ == "__main__":
    main()