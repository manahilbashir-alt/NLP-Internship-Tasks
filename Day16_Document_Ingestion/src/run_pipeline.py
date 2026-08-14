"""
Day 16 - Main pipeline runner.

For each source document (native.pdf, document.docx, document.txt):
  - ingest it
  - run all 5 chunking strategies
  - attach metadata: source_filename, page_number, chunk_index, section_heading
  - verify that every chunk kept its source_filename (metadata integrity check)

Chunking strategy used for the metadata-integrity table (Section 4/Section
"Metadata Verification" of the report) is the Recursive strategy, since it
is the general-purpose default; all 5 strategies are still benchmarked and
compared in Section 3.
"""

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))

from ingestion import ingest_pdf_pdfplumber, ingest_pdf_pypdf2, ingest_docx, ingest_txt
from chunking import (
    chunk_fixed_size,
    chunk_token_based,
    chunk_recursive,
    chunk_semantic,
    chunk_hierarchical,
)

DATA = "/home/claude/day16_project/data"
OUT = "/home/claude/day16_project/output"
os.makedirs(f"{OUT}/chunks", exist_ok=True)

RESULTS = {}


# ---------------------------------------------------------------------------
# Helper: build metadata-tagged chunks for a flat list of raw text chunks
# ---------------------------------------------------------------------------
def tag_chunks(raw_chunks, source_filename, page_number=None, section_heading="Unknown"):
    tagged = []
    for i, text in enumerate(raw_chunks):
        tagged.append(
            {
                "text": text,
                "metadata": {
                    "source_filename": source_filename,
                    "page_number": page_number,
                    "chunk_index": i,
                    "section_heading": section_heading,
                },
            }
        )
    return tagged


# ---------------------------------------------------------------------------
# 1. PDF ingestion (both engines) + chunking (per-page, all 5 strategies)
# ---------------------------------------------------------------------------
print("=" * 70)
print("PDF INGESTION")
print("=" * 70)

t0 = time.time()
plumber_pages = ingest_pdf_pdfplumber(f"{DATA}/native.pdf")
t_plumber = time.time() - t0

t0 = time.time()
pypdf2_pages = ingest_pdf_pypdf2(f"{DATA}/native.pdf")
t_pypdf2 = time.time() - t0

print(f"PDFPlumber: {len(plumber_pages)} pages in {t_plumber:.2f}s")
print(f"PyPDF2:     {len(pypdf2_pages)} pages in {t_pypdf2:.2f}s")

RESULTS["pdf_ingestion"] = {
    "source": "native.pdf",
    "pages_pdfplumber": len(plumber_pages),
    "pages_pypdf2": len(pypdf2_pages),
    "time_pdfplumber_sec": round(t_plumber, 3),
    "time_pypdf2_sec": round(t_pypdf2, 3),
}

# Chunk the PDF (using PDFPlumber output, tracking real page numbers) with
# each strategy. This is the main "chunk volume" pass used for metadata
# verification and strategy comparison across the whole 56-page document.
pdf_full_text = "\n\n".join(p["text"] for p in plumber_pages)

strategies = {
    "fixed_size": lambda t: chunk_fixed_size(t, chunk_size=500, overlap=50),
    "token_based": lambda t: chunk_token_based(t, chunk_size=200, overlap=20),
    "recursive": lambda t: chunk_recursive(t, chunk_size=500, overlap=50),
    "semantic": lambda t: chunk_semantic(t, similarity_threshold=0.15, min_sentences=2, max_chunk_chars=1200),
}

pdf_chunk_counts = {}
pdf_chunks_by_strategy = {}

for name, fn in strategies.items():
    t0 = time.time()
    # Chunk per-page so page_number metadata stays accurate
    all_chunks = []
    for page in plumber_pages:
        if not page["text"].strip():
            continue
        raw_chunks = fn(page["text"])
        tagged = tag_chunks(
            raw_chunks,
            source_filename="native.pdf",
            page_number=page["page_number"],
            section_heading="Unknown",
        )
        all_chunks.extend(tagged)
    # Fix chunk_index to be global, not per-page
    for i, c in enumerate(all_chunks):
        c["metadata"]["chunk_index"] = i
    elapsed = time.time() - t0
    pdf_chunk_counts[name] = len(all_chunks)
    pdf_chunks_by_strategy[name] = all_chunks
    print(f"PDF / {name:12s}: {len(all_chunks):5d} chunks in {elapsed:.2f}s")

# Hierarchical strategy needs document structure -- PDFs here have no
# reliable structure tags, so we approximate sections using the ALL-CAPS
# chapter heading lines our generator wrote at the top of each chapter.
import re


def hierarchical_chunks_for_pdf(pages, chunk_size=500, overlap=50):
    current_section = "Document Start"
    buffer = []
    sections = []

    def flush():
        if buffer:
            sections.append({"section": current_section, "text": " ".join(buffer)})
            buffer.clear()

    heading_re = re.compile(r"^[A-Z][A-Z0-9 ,'\-]{4,60}$")
    for page in pages:
        for line in page["text"].split("\n"):
            line = line.strip()
            if not line:
                continue
            if heading_re.match(line) and len(line.split()) <= 8:
                flush()
                current_section = line.title()
            else:
                buffer.append(line)
    flush()

    chunks = []
    for sec in sections:
        for piece in chunk_fixed_size(sec["text"], chunk_size=chunk_size, overlap=overlap):
            if piece.strip():
                chunks.append({"text": piece, "section_heading": sec["section"]})
    return chunks


t0 = time.time()
hier_raw = hierarchical_chunks_for_pdf(plumber_pages)
hier_tagged = []
for i, c in enumerate(hier_raw):
    hier_tagged.append(
        {
            "text": c["text"],
            "metadata": {
                "source_filename": "native.pdf",
                "page_number": None,  # spans a section, not one page
                "chunk_index": i,
                "section_heading": c["section_heading"],
            },
        }
    )
elapsed = time.time() - t0
pdf_chunk_counts["hierarchical"] = len(hier_tagged)
pdf_chunks_by_strategy["hierarchical"] = hier_tagged
print(f"PDF / {'hierarchical':12s}: {len(hier_tagged):5d} chunks in {elapsed:.2f}s")

RESULTS["pdf_chunk_counts"] = pdf_chunk_counts

# ---------------------------------------------------------------------------
# 2. DOCX ingestion + hierarchical chunking (true heading structure) +
#    other strategies for comparison
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("DOCX INGESTION")
print("=" * 70)

t0 = time.time()
docx_paras = ingest_docx(f"{DATA}/document.docx")
t_docx = time.time() - t0
n_headings = sum(1 for p in docx_paras if p["is_heading"])
print(f"python-docx: {len(docx_paras)} paragraphs ({n_headings} headings) in {t_docx:.2f}s")

RESULTS["docx_ingestion"] = {
    "source": "document.docx",
    "paragraphs_extracted": len(docx_paras),
    "headings_found": n_headings,
    "time_sec": round(t_docx, 3),
}

docx_full_text = "\n\n".join(p["text"] for p in docx_paras if not p["is_heading"])

docx_chunk_counts = {}
docx_chunks_by_strategy = {}

for name, fn in strategies.items():
    t0 = time.time()
    raw_chunks = fn(docx_full_text)
    tagged = tag_chunks(raw_chunks, source_filename="document.docx", page_number=None, section_heading="Unknown")
    elapsed = time.time() - t0
    docx_chunk_counts[name] = len(tagged)
    docx_chunks_by_strategy[name] = tagged
    print(f"DOCX / {name:12s}: {len(tagged):5d} chunks in {elapsed:.2f}s")

t0 = time.time()
hier_docx_raw = chunk_hierarchical(docx_paras, chunk_size=500, overlap=50)
hier_docx_tagged = []
for i, c in enumerate(hier_docx_raw):
    hier_docx_tagged.append(
        {
            "text": c["text"],
            "metadata": {
                "source_filename": "document.docx",
                "page_number": None,
                "chunk_index": i,
                "section_heading": c["section_heading"],
                "subsection_heading": c["subsection_heading"],
            },
        }
    )
elapsed = time.time() - t0
docx_chunk_counts["hierarchical"] = len(hier_docx_tagged)
docx_chunks_by_strategy["hierarchical"] = hier_docx_tagged
print(f"DOCX / {'hierarchical':12s}: {len(hier_docx_tagged):5d} chunks in {elapsed:.2f}s (TRUE heading structure)")

RESULTS["docx_chunk_counts"] = docx_chunk_counts

# ---------------------------------------------------------------------------
# 3. TXT ingestion + chunking
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("TXT INGESTION")
print("=" * 70)

t0 = time.time()
txt_text = ingest_txt(f"{DATA}/document.txt")
t_txt = time.time() - t0
print(f"Plain read: {len(txt_text)} characters in {t_txt:.3f}s")

RESULTS["txt_ingestion"] = {
    "source": "document.txt",
    "characters_extracted": len(txt_text),
    "time_sec": round(t_txt, 3),
}

txt_chunk_counts = {}
txt_chunks_by_strategy = {}
for name, fn in strategies.items():
    t0 = time.time()
    raw_chunks = fn(txt_text)
    tagged = tag_chunks(raw_chunks, source_filename="document.txt", page_number=None, section_heading="Unknown")
    elapsed = time.time() - t0
    txt_chunk_counts[name] = len(tagged)
    txt_chunks_by_strategy[name] = tagged
    print(f"TXT / {name:12s}: {len(tagged):5d} chunks in {elapsed:.2f}s")

RESULTS["txt_chunk_counts"] = txt_chunk_counts

# ---------------------------------------------------------------------------
# 4. Metadata integrity verification (across all 3 doc types, recursive
#    strategy chosen as the representative "production" pass)
# ---------------------------------------------------------------------------
print()
print("=" * 70)
print("METADATA VERIFICATION (recursive strategy)")
print("=" * 70)

verification = {}
for label, chunks in [
    ("PDF", pdf_chunks_by_strategy["recursive"]),
    ("DOCX", docx_chunks_by_strategy["recursive"]),
    ("TXT", txt_chunks_by_strategy["recursive"]),
]:
    total = len(chunks)
    missing_source = sum(1 for c in chunks if not c["metadata"].get("source_filename"))
    passed = missing_source == 0
    verification[label] = {
        "chunks": total,
        "missing_source_filename": missing_source,
        "status": "PASS" if passed else "FAIL",
    }
    print(f"{label:5s} | chunks={total:5d} | missing_source_filename={missing_source} | {'PASS' if passed else 'FAIL'}")

RESULTS["metadata_verification"] = verification

# ---------------------------------------------------------------------------
# Save everything to output/
# ---------------------------------------------------------------------------
with open(f"{OUT}/chunks/pdf_recursive_chunks.json", "w") as f:
    json.dump(pdf_chunks_by_strategy["recursive"][:20], f, indent=2)  # sample
with open(f"{OUT}/chunks/docx_hierarchical_chunks.json", "w") as f:
    json.dump(docx_chunks_by_strategy["hierarchical"], f, indent=2)
with open(f"{OUT}/chunks/txt_recursive_chunks.json", "w") as f:
    json.dump(txt_chunks_by_strategy["recursive"][:20], f, indent=2)  # sample

with open(f"{OUT}/pipeline_results.json", "w") as f:
    json.dump(RESULTS, f, indent=2)

print()
print("Saved pipeline_results.json and sample chunk files to output/")
print(json.dumps(RESULTS, indent=2))
