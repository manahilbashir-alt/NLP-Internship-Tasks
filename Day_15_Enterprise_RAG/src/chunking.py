"""
chunking.py

Recursive splitter: try to cut on paragraph breaks first, fall back to
sentences, fall back to raw character windows only if a single sentence
is somehow still too long (rare, but a giant table row will do it).

This is the same idea LangChain's RecursiveCharacterTextSplitter uses -
no need to reinvent it, just don't want the extra dependency for one
function.
"""

from dataclasses import dataclass, field
from typing import Optional

from src.ingestion import Document

PARA_BREAK = "\n\n"
SENTENCE_SPLIT = ". "


@dataclass
class Chunk:
    text: str
    source: str
    chunk_id: str
    metadata: dict = field(default_factory=dict)


def _split_on(text: str, sep: str, max_len: int) -> list[str]:
    pieces = text.split(sep)
    out, current = [], ""
    for p in pieces:
        candidate = (current + sep + p) if current else p
        if len(candidate) <= max_len:
            current = candidate
        else:
            if current:
                out.append(current)
            current = p if len(p) <= max_len else p  # oversized piece handled by caller
    if current:
        out.append(current)
    return out


def recursive_split(text: str, max_len: int = 800) -> list[str]:
    if len(text) <= max_len:
        return [text] if text.strip() else []

    chunks = []
    for para in _split_on(text, PARA_BREAK, max_len):
        if len(para) <= max_len:
            chunks.append(para)
        else:
            for sent_chunk in _split_on(para, SENTENCE_SPLIT, max_len):
                if len(sent_chunk) <= max_len:
                    chunks.append(sent_chunk)
                else:
                    # last resort: hard character window
                    for i in range(0, len(sent_chunk), max_len):
                        chunks.append(sent_chunk[i:i + max_len])
    return [c.strip() for c in chunks if c.strip()]


def add_overlap(chunks: list[str], overlap_chars: int = 120) -> list[str]:
    """Prepend a tail of the previous chunk so a fact split across a
    boundary still has a fighting chance of showing up whole in one of
    the two chunks."""
    if overlap_chars <= 0 or len(chunks) < 2:
        return chunks
    out = [chunks[0]]
    for i in range(1, len(chunks)):
        tail = chunks[i - 1][-overlap_chars:]
        out.append(tail + " " + chunks[i])
    return out


def chunk_document(doc: Document, max_len: int = 800, overlap_chars: int = 120) -> list[Chunk]:
    raw_chunks = recursive_split(doc.text, max_len=max_len)
    raw_chunks = add_overlap(raw_chunks, overlap_chars=overlap_chars)

    chunks = []
    for i, text in enumerate(raw_chunks):
        chunks.append(Chunk(
            text=text,
            source=doc.source,
            chunk_id=f"{doc.metadata.get('filename', doc.source)}::chunk_{i}",
            metadata={**doc.metadata, "chunk_index": i},
        ))
    return chunks


def chunk_corpus(docs: list[Document], max_len: int = 800, overlap_chars: int = 120) -> list[Chunk]:
    all_chunks = []
    for doc in docs:
        all_chunks.extend(chunk_document(doc, max_len=max_len, overlap_chars=overlap_chars))
    return all_chunks


if __name__ == "__main__":
    from ingestion import load_corpus
    docs = load_corpus("data/corpus")
    chunks = chunk_corpus(docs)
    print(f"{len(docs)} docs -> {len(chunks)} chunks")
    if chunks:
        print("--- sample chunk ---")
        print(chunks[0].chunk_id)
        print(chunks[0].text[:300])
