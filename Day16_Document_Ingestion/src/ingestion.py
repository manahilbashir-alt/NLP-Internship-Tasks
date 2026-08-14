"""
Day 16 - Step 1: Document Ingestion

Implements ingestion pipelines for:
  - PDF via PDFPlumber
  - PDF via PyPDF2
  - DOCX via python-docx
  - Plain TXT
"""

import pdfplumber
import PyPDF2
import docx


def ingest_pdf_pdfplumber(path):
    """Extract text page-by-page using PDFPlumber. Returns list of dicts."""
    pages = []
    with pdfplumber.open(path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages.append({"page_number": i + 1, "text": text})
    return pages


def ingest_pdf_pypdf2(path):
    """Extract text page-by-page using PyPDF2. Returns list of dicts."""
    pages = []
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append({"page_number": i + 1, "text": text})
    return pages


def ingest_docx(path):
    """
    Extract paragraphs using python-docx, preserving heading styles.
    Returns list of dicts: {paragraph_index, text, style, is_heading, heading_level}
    """
    d = docx.Document(path)
    paragraphs = []
    current_heading = "Unknown"
    for i, p in enumerate(d.paragraphs):
        text = p.text.strip()
        if not text:
            continue
        style_name = p.style.name if p.style else "Normal"
        is_heading = style_name.lower().startswith("heading") or style_name.lower() == "title"
        if is_heading:
            current_heading = text
        paragraphs.append(
            {
                "paragraph_index": i,
                "text": text,
                "style": style_name,
                "is_heading": is_heading,
                "section_heading": current_heading,
            }
        )
    return paragraphs


def ingest_txt(path):
    """Extract raw text from a plain .txt file."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return text


if __name__ == "__main__":
    DATA = "/home/claude/day16_project/data"

    plumber_pages = ingest_pdf_pdfplumber(f"{DATA}/native.pdf")
    pypdf2_pages = ingest_pdf_pypdf2(f"{DATA}/native.pdf")
    docx_paras = ingest_docx(f"{DATA}/document.docx")
    txt_text = ingest_txt(f"{DATA}/document.txt")

    print("=== PDF Result ===")
    print(f"Source: native.pdf")
    print(f"PDFPlumber pages extracted: {len(plumber_pages)}")
    print(f"PyPDF2 pages extracted:     {len(pypdf2_pages)}")
    print(f"Sample (PDFPlumber, page 1, first 150 chars):")
    print(plumber_pages[0]["text"][:150].replace("\n", " "))

    print("\n=== DOCX Result ===")
    print(f"Source: document.docx")
    print(f"Paragraphs extracted: {len(docx_paras)}")
    n_headings = sum(1 for p in docx_paras if p["is_heading"])
    print(f"Heading paragraphs found: {n_headings}")

    print("\n=== TXT Result ===")
    print(f"Source: document.txt")
    print(f"Characters extracted: {len(txt_text)}")
