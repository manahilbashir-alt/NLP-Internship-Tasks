"""
Day 16 - Step 2: OCR Pipeline

Implements OCR-based ingestion for scanned (image-only) PDFs using
pytesseract + Tesseract OCR, and compares text quality against native
PDF extraction for the same underlying pages.
"""

import difflib
import pytesseract
from pdf2image import convert_from_path
import pdfplumber
import subprocess

DATA = "/home/claude/day16_project/data"


def get_tesseract_version():
    out = subprocess.run(["tesseract", "--version"], capture_output=True, text=True)
    return out.stdout.splitlines()[0] if out.stdout else "unknown"


def ocr_pdf(path):
    """OCR every page of an image-only PDF. Returns list of dicts."""
    images = convert_from_path(path, dpi=200)
    pages = []
    for i, img in enumerate(images):
        text = pytesseract.image_to_string(img)
        pages.append({"page_number": i + 1, "text": text})
    return pages


def native_text_for_first_n_pages(path, n):
    pages = []
    with pdfplumber.open(path) as pdf:
        for i in range(n):
            text = pdf.pages[i].extract_text() or ""
            pages.append({"page_number": i + 1, "text": text})
    return pages


def similarity(a, b):
    return difflib.SequenceMatcher(None, a, b).ratio()


if __name__ == "__main__":
    print(f"Tesseract version: {get_tesseract_version()}")

    scanned_pages = ocr_pdf(f"{DATA}/scanned.pdf")
    native_pages = native_text_for_first_n_pages(f"{DATA}/native.pdf", len(scanned_pages))

    print(f"\nOCR pages processed: {len(scanned_pages)}")

    print("\n=== Native vs OCR comparison (per page) ===")
    total_sim = 0
    for nat, ocr in zip(native_pages, scanned_pages):
        sim = similarity(nat["text"], ocr["text"])
        total_sim += sim
        print(f"Page {nat['page_number']}: similarity={sim:.3f}  "
              f"native_chars={len(nat['text'])}  ocr_chars={len(ocr['text'])}")

    avg_sim = total_sim / len(scanned_pages)
    print(f"\nAverage native-vs-OCR text similarity: {avg_sim:.3f}")

    print("\n--- Native extraction sample (page 1, first 200 chars) ---")
    print(repr(native_pages[0]["text"][:200]))
    print("\n--- OCR extraction sample (page 1, first 200 chars) ---")
    print(repr(scanned_pages[0]["text"][:200]))
