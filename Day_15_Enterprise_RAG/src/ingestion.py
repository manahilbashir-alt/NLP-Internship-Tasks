"""
ingestion.py

Turns raw files into (text, metadata) records. Two parsers are wired up:
pypdf for a fast first pass, pdfplumber when we need tables/layout to
survive. Plain text and markdown just get read and cleaned.

Everything downstream (chunking, embedding) expects a list of Document
objects out of this module, so treat that as the contract.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import re

import pypdf
import pdfplumber


@dataclass
class Document:
    text: str
    source: str
    doc_type: str
    metadata: dict = field(default_factory=dict)


def _clean(text: str) -> str:
    # de-hyphenate words split across a line break: "informa-\ntion" -> "information"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # collapse the repeated blank lines PDF extraction tends to leave behind
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def load_pdf(path: str, use_pdfplumber: bool = False) -> Document:
    """
    use_pdfplumber=True is slower but keeps tables readable, which pypdf
    tends to mangle. Default to pypdf for straight text-heavy PDFs.
    """
    path = Path(path)
    pages = []

    if use_pdfplumber:
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text() or ""
                tables = page.extract_tables()
                for t in tables:
                    # flatten tables to pipe-separated rows so at least the
                    # values survive, rather than dropping them silently
                    rows = [" | ".join(cell or "" for cell in row) for row in t]
                    page_text += "\n" + "\n".join(rows)
                pages.append((i + 1, page_text))
    else:
        reader = pypdf.PdfReader(str(path))
        for i, page in enumerate(reader.pages):
            pages.append((i + 1, page.extract_text() or ""))

    full_text = "\n\n".join(f"[page {n}]\n{_clean(t)}" for n, t in pages if t.strip())

    return Document(
        text=full_text,
        source=str(path),
        doc_type="pdf",
        metadata={"num_pages": len(pages), "filename": path.name},
    )


def load_text(path: str) -> Document:
    path = Path(path)
    raw = path.read_text(encoding="utf-8", errors="ignore")
    return Document(
        text=_clean(raw),
        source=str(path),
        doc_type=path.suffix.lstrip(".") or "text",
        metadata={"filename": path.name},
    )


def load_corpus(corpus_dir: str) -> list[Document]:
    """Walk a directory and load everything we know how to parse. Anything
    else gets skipped with a note rather than crashing the whole run —
    a single bad file shouldn't take down an ingestion job."""
    corpus_dir = Path(corpus_dir)
    docs = []
    skipped = []

    for path in sorted(corpus_dir.rglob("*")):
        if path.is_dir():
            continue
        suffix = path.suffix.lower()
        try:
            if suffix == ".pdf":
                docs.append(load_pdf(path))
            elif suffix in (".txt", ".md"):
                docs.append(load_text(path))
            else:
                skipped.append(str(path))
        except Exception as e:
            skipped.append(f"{path} (error: {e})")

    if skipped:
        print(f"[ingestion] skipped {len(skipped)} file(s): {skipped}")

    return docs


if __name__ == "__main__":
    import sys
    corpus_path = sys.argv[1] if len(sys.argv) > 1 else "data/corpus"
    docs = load_corpus(corpus_path)
    for d in docs:
        print(f"{d.source}: {len(d.text)} chars, type={d.doc_type}")
