"""
================================================================================
 DAY 17 - STAGE 2: RECURSIVE CHUNKING (manual splitter + rich metadata)
================================================================================
WHAT THIS FILE DOES:
  Reads data/structured.md (produced by ingestion/ingestion_pipeline.py)
  and cuts it into small, meaningful pieces called "chunks" - the units
  we will feed into embedding models next.

WHAT "RECURSIVE" CHUNKING MEANS (plain words):
  We don't just cut every N characters (that can slice a sentence in half).
  Instead we try big natural breakpoints FIRST, and only fall back to a
  smaller breakpoint if a piece is still too large:
      1st try: paragraph breaks ("\n\n")
      2nd try: line breaks ("\n")
      3rd try: sentence ends (". ")
      4th try: spaces (word boundaries)
      last resort: hard cut by raw character count

  Each chunk also OVERLAPS a little with the next one (default 100 chars),
  so an idea that gets cut right at a chunk boundary isn't fully lost.

WHY WE PARSE THE MARKDOWN OURSELVES FIRST:
  We need to know page/section/type per block, and tables/images/formulas
  must NEVER be split apart. So we do a first pass (parse_markdown_into_blocks)
  to figure that out, THEN run our own recursive_split() on just the plain
  "text" blocks.

METADATA ATTACHED TO EVERY CHUNK:
  - chunk_id       : unique id (e.g. "chunk_0007")
  - chunk_index    : position in the whole document (0, 1, 2, ...)
  - source_file    : which PDF this came from
  - page_no        : which PDF page this chunk starts on
  - section        : nearest heading above this chunk (e.g. "Evaluation Metrics")
  - chunk_type     : "text" | "table" | "image" | "formula" (auto-detected)
  - char_count     : how many characters in this chunk
  - word_count     : how many words in this chunk
  - prev_chunk_id  : id of the chunk right before this one (or null)
  - next_chunk_id  : id of the chunk right after this one (or null)

PROJECT LAYOUT THIS SCRIPT ASSUMES (run it from the project root):
  day17_embeddings_vector_db/
    data/
      structured.md            <- input (from Stage 1, saved next to the PDF)
      images/
    chunking/
      recursive_chunker.py      <- this file
      chunks.json                <- output (created here)

HOW TO RUN (from project root, with venv17 active):
  pip install langchain-text-splitters --break-system-packages
  python chunking/recursive_chunker.py
================================================================================
"""

import json
import re
from pathlib import Path

# ------------------------------------------------------------------------
# CONFIG - paths are relative to the PROJECT ROOT, not to this file.
# Always run this script from the project root folder.
# ------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCE_MD_PATH = PROJECT_ROOT / "data" / "structured.md"
SOURCE_FILENAME = "MACHINE LEARNING.pdf"   # original PDF name, stored in metadata
CHUNKING_DIR = PROJECT_ROOT / "chunking"
CHUNKS_OUTPUT_PATH = CHUNKING_DIR / "chunks.json"

CHUNK_SIZE = 800       # target max characters per chunk
CHUNK_OVERLAP = 100    # characters repeated between consecutive chunks

# The order we try to split on, biggest/most-meaningful breakpoint first.
SEPARATORS = ["\n\n", "\n", ". ", " "]


# ------------------------------------------------------------------------
# STEP A: Parse the markdown into (page_no, section, text_block) pieces
# ------------------------------------------------------------------------
def parse_markdown_into_blocks(markdown_text: str):
    """
    Walks through structured.md line by line.
    Tracks the current page number (from hidden <!-- page:N --> markers)
    and the current section heading (from "## " lines).
    Returns a list of blocks: {"page_no": int, "section": str, "text": str,
    "block_type": str} where tables/images/formulas become their own
    dedicated block (never mixed with surrounding text).
    """
    page_marker_re = re.compile(r"<!--\s*page:(\d+)\s*-->")
    heading_re = re.compile(r"^##\s+(.*)$")
    table_row_re = re.compile(r"^\|.*\|$")
    image_re = re.compile(r"^!\[.*\]\(.*\)$")
    formula_start_re = re.compile(r"^\$\$$")

    blocks = []
    current_page = None
    current_section = "Introduction"
    buffer_lines = []

    def flush_buffer(block_type="text"):
        text = "\n".join(buffer_lines).strip()
        if text:
            blocks.append({
                "page_no": current_page,
                "section": current_section,
                "text": text,
                "block_type": block_type,
            })
        buffer_lines.clear()

    lines = markdown_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]

        page_match = page_marker_re.search(line)
        if page_match:
            flush_buffer()
            current_page = int(page_match.group(1))
            i += 1
            continue

        heading_match = heading_re.match(line)
        if heading_match:
            flush_buffer()
            current_section = heading_match.group(1).strip()
            i += 1
            continue

        if table_row_re.match(line.strip()):
            flush_buffer()
            table_lines = []
            while i < len(lines) and table_row_re.match(lines[i].strip()):
                table_lines.append(lines[i])
                i += 1
            blocks.append({
                "page_no": current_page, "section": current_section,
                "text": "\n".join(table_lines), "block_type": "table",
            })
            continue

        if image_re.match(line.strip()):
            flush_buffer()
            blocks.append({
                "page_no": current_page, "section": current_section,
                "text": line.strip(), "block_type": "image",
            })
            i += 1
            continue

        if formula_start_re.match(line.strip()):
            flush_buffer()
            formula_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip() != "$$":
                formula_lines.append(lines[i])
                i += 1
            if i < len(lines):
                formula_lines.append(lines[i])
                i += 1
            blocks.append({
                "page_no": current_page, "section": current_section,
                "text": "\n".join(formula_lines), "block_type": "formula",
            })
            continue

        buffer_lines.append(line)
        i += 1

    flush_buffer()
    return blocks


# ------------------------------------------------------------------------
# STEP B: Recursive splitter - cuts long text blocks into smaller pieces
# ------------------------------------------------------------------------
def recursive_split(text: str, separators: list, chunk_size: int) -> list:
    """
    Tries to split `text` using the first separator in the list.
    If a resulting piece is still bigger than chunk_size, it recursively
    tries the NEXT separator on just that piece. If we run out of
    separators, it hard-cuts by character count as a last resort.
    """
    if len(text) <= chunk_size:
        return [text]

    if not separators:
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    sep = separators[0]
    remaining_separators = separators[1:]

    pieces = text.split(sep)
    results = []
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        if len(piece) <= chunk_size:
            results.append(piece)
        else:
            results.extend(recursive_split(piece, remaining_separators, chunk_size))
    return results


def add_overlap(pieces: list, overlap: int) -> list:
    """
    Adds a bit of repeated text between consecutive pieces, so context
    isn't fully lost at a chunk boundary.
    """
    if overlap <= 0 or len(pieces) <= 1:
        return pieces

    overlapped = [pieces[0]]
    for i in range(1, len(pieces)):
        prev_tail = pieces[i - 1][-overlap:]
        overlapped.append(prev_tail + " " + pieces[i])
    return overlapped


# ------------------------------------------------------------------------
# STEP C: Build final chunks with rich metadata
# ------------------------------------------------------------------------
def build_chunks(blocks: list) -> list:
    chunks = []

    for block in blocks:
        block_type = block["block_type"]

        if block_type in ("table", "image", "formula"):
            # Never split these - they must stay whole to make sense.
            pieces = [block["text"]]
        else:
            raw_pieces = recursive_split(block["text"], SEPARATORS, CHUNK_SIZE)
            pieces = add_overlap(raw_pieces, CHUNK_OVERLAP)

        for piece in pieces:
            chunks.append({
                "chunk_id": None,        # filled in after we know final order
                "chunk_index": None,
                "source_file": SOURCE_FILENAME,
                "page_no": block["page_no"],
                "section": block["section"],
                "chunk_type": block_type,
                "content": piece,
                "char_count": len(piece),
                "word_count": len(piece.split()),
                "prev_chunk_id": None,
                "next_chunk_id": None,
            })

    # Assign sequential ids and link prev/next neighbors
    for idx, chunk in enumerate(chunks):
        chunk["chunk_index"] = idx
        chunk["chunk_id"] = f"chunk_{idx:04d}"

    for idx, chunk in enumerate(chunks):
        chunk["prev_chunk_id"] = chunks[idx - 1]["chunk_id"] if idx > 0 else None
        chunk["next_chunk_id"] = chunks[idx + 1]["chunk_id"] if idx < len(chunks) - 1 else None

    return chunks


def main():
    CHUNKING_DIR.mkdir(exist_ok=True)

    if not SOURCE_MD_PATH.exists():
        print(f"[error] {SOURCE_MD_PATH} not found. Run ingestion/ingestion_pipeline.py first.")
        return

    markdown_text = SOURCE_MD_PATH.read_text(encoding="utf-8")
    print(f"[load] Read {len(markdown_text)} characters from {SOURCE_MD_PATH}")

    blocks = parse_markdown_into_blocks(markdown_text)
    print(f"[parse] Found {len(blocks)} content blocks")

    chunks = build_chunks(blocks)
    print(f"[chunk] Produced {len(chunks)} final chunks")

    counts = {}
    for c in chunks:
        counts[c["chunk_type"]] = counts.get(c["chunk_type"], 0) + 1
    print(f"[chunk] Breakdown by type: {counts}")

    CHUNKS_OUTPUT_PATH.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"[save] Chunks with metadata written to: {CHUNKS_OUTPUT_PATH}")
    print("\n[done] Stage 2 complete. Next: embed these chunks (Step 3).")


if __name__ == "__main__":
    main()


def chunk_markdown_text(markdown_text: str, source_filename: str, start_index: int = 0) -> list:
    """
    Same chunking logic as build_chunks(), but for arbitrary markdown text
    with a caller-supplied source filename and a starting chunk_index —
    so new chunks never collide with IDs already in the FAISS index.
    Used by /api/rag/ingest for user-uploaded documents.
    """
    blocks = parse_markdown_into_blocks(markdown_text)
    chunks = []

    for block in blocks:
        block_type = block["block_type"]
        if block_type in ("table", "image", "formula"):
            pieces = [block["text"]]
        else:
            raw_pieces = recursive_split(block["text"], SEPARATORS, CHUNK_SIZE)
            pieces = add_overlap(raw_pieces, CHUNK_OVERLAP)

        for piece in pieces:
            chunks.append({
                "chunk_id": None, "chunk_index": None,
                "source_file": source_filename,
                "page_no": block["page_no"], "section": block["section"],
                "chunk_type": block_type, "content": piece,
                "char_count": len(piece), "word_count": len(piece.split()),
                "prev_chunk_id": None, "next_chunk_id": None,
            })

    for offset, chunk in enumerate(chunks):
        idx = start_index + offset
        chunk["chunk_index"] = idx
        chunk["chunk_id"] = f"chunk_{idx:04d}"
    for offset, chunk in enumerate(chunks):
        chunk["prev_chunk_id"] = chunks[offset - 1]["chunk_id"] if offset > 0 else None
        chunk["next_chunk_id"] = chunks[offset + 1]["chunk_id"] if offset < len(chunks) - 1 else None

    return chunks