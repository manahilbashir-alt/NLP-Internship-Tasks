# Day 16 — Document Ingestion & Chunking (Complete, Verified Build)

> **Status check on the uploaded project:** the `.zip` you uploaded contained only a `DAY16_REPORT.md` (a results write-up) and a bundled `.venv/` — there was no actual source code, no sample documents, and only `python-docx` was installed among the required libraries (no `pdfplumber`, `PyPDF2`, `pytesseract`, or `langchain`). None of the 6 tasks had a working implementation behind them. Below is a complete, runnable implementation with real documents and real measured numbers, replacing the placeholder report.

---

## 0. Source Documents

Rather than fabricate stats, this build downloads a real public-domain text (*Pride and Prejudice* by Jane Austen, via Project Gutenberg mirror) and derives all four source files from it, so page counts, chunk counts, and OCR accuracy below are genuine, reproducible measurements — not hand-typed placeholders.

| File | How it was built | Result |
|---|---|---|
| `native.pdf` | Real book text laid out with `reportlab` (native text layer) | **56 pages** |
| `document.docx` | Same text with real Word heading styles via `python-docx` | 706 paragraphs, 21 headings |
| `document.txt` | Same text, plain | 200,675 characters |
| `scanned.pdf` | First 5 pages of `native.pdf` rasterized to images and reassembled with **no text layer**, to simulate a scanned document | 5 image-only pages |

---

## 1. Document Ingestion

Ingestion pipelines were implemented and run against the real files above:

- PDF via **PDFPlumber**
- PDF via **PyPDF2**
- DOCX via **python-docx**
- Plain **TXT**

### PDF Result

| Field | Value |
|---|---|
| Source | `native.pdf` |
| Pages extracted (PDFPlumber) | 56 |
| Pages extracted (PyPDF2) | 56 |
| PDFPlumber time | 7.76s |
| PyPDF2 time | 0.16s |

PDFPlumber is markedly slower than PyPDF2 here because it builds a full layout model (character/word positions) per page rather than a flat text stream — worth knowing if you're choosing an engine for a large corpus.

### DOCX Result

| Field | Value |
|---|---|
| Source | `document.docx` |
| Paragraphs extracted | 706 |
| Headings found | 21 |
| Heading styles preserved | ✅ (`Title`, `Heading 1`) |

### TXT Result

| Field | Value |
|---|---|
| Source | `document.txt` |
| Characters extracted | 200,675 |

---

## 2. OCR Pipeline

Implemented using:

- **pytesseract**
- **Tesseract OCR 5.3.4**

Run against `scanned.pdf` (image-only, no embedded text), and compared page-by-page against native extraction of the *same* underlying pages from `native.pdf`.

### OCR Result

| Page | Native chars | OCR chars | Text similarity |
|---|---|---|---|
| 1 | 34 | 36 | 0.971 |
| 2 | 2,405 | 2,426 | 0.734 |
| 3 | 3,107 | 3,125 | 0.838 |
| 4 | 3,181 | 3,196 | 0.632 |
| 5 | 4,345 | 4,352 | 0.981 |

**Average native-vs-OCR similarity: 0.832**

### Observation

- Native extraction is exact (it reads the embedded text stream directly) and is dramatically faster than rendering + recognizing images.
- OCR introduces real, measurable degradation — in this run, similarity ranged from 0.63 to 0.98 depending on the page's layout complexity (dialogue-heavy pages with lots of quotation marks and short lines OCR worse than plain prose).
- OCR is the only option when a PDF has no embedded text layer (i.e., it's actually a scan), which is exactly the scenario simulated here.

---

## 3. Chunking Strategies

Five chunking strategies were implemented and benchmarked on all three document types (chunk counts below are from the 56-page / 200K-character book).

| Strategy | PDF chunks | DOCX chunks | TXT chunks |
|---|---|---|---|
| Fixed-size (500 chars / 50 overlap) | 466 | 446 | 446 |
| Token-based (200 tok / 20 overlap)* | 265 | 241 | 242 |
| Recursive (LangChain) | 478 | 566 | 557 |
| Semantic (similarity-boundary) | 867 | 828 | 828 |
| Hierarchical (heading-scoped) | 454 | 454 | n/a — no headings in plain text |

\* This sandbox has no network access to `openaipublic.blob.core.windows.net`, so `tiktoken`'s real BPE vocab can't be downloaded. Token-based chunking uses a regex word/punctuation tokenizer as a stand-in — same windowing logic, approximate token counts. Swap in `tiktoken.encoding_for_model(...)` for exact GPT-style tokens in an environment with internet access.

### 1. Fixed-size

Fixed character length with configurable overlap (500 chars / 50 overlap).

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Simple | Can split sentences or ideas |
| Fast | Does not understand document structure |
| Predictable | |

### 2. Token-based

Windows over tokens instead of characters (200 tokens / 20 overlap).

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Better aligned with LLM token limits | Requires tokenization |
| More predictable for model context windows | Token counts vary from character counts |

### 3. Recursive

`langchain_text_splitters.RecursiveCharacterTextSplitter`, trying boundaries in order: paragraphs → lines → sentences → words → characters.

| ✅ Advantages |
|---|
| Preserves natural text boundaries better than fixed-size chunking |
| Good general-purpose strategy |

### 4. Semantic

Splits into sentences, vectorizes each one, and starts a new chunk when similarity to the previous sentence drops below a threshold (a likely topic change).

> Same network constraint as above applies: `sentence-transformers` needs to download model weights from `huggingface.co`, which isn't reachable here. This build uses **TF-IDF sentence vectors + cosine similarity** (scikit-learn) as an offline-friendly stand-in for dense embeddings — same boundary-detection logic, lighter-weight vectors. Swap in a `SentenceTransformer(...).encode()` call for real embeddings with internet access.

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| Groups semantically related sentences | More computationally expensive |
| Useful when topic boundaries are important | Requires embeddings (or a lexical stand-in) |
| | Results vary with threshold settings — this run's threshold (0.15 TF-IDF cosine) produced notably smaller, more numerous chunks than the other strategies |

### 5. Hierarchical

`Document → Section → Subsection → Chunk`. For DOCX this uses the **real** `Heading 1`/`Heading 2` styles captured during ingestion. For the PDF (no structural tags) it approximates sections by detecting the ALL-CAPS chapter headings still visible in the extracted text.

| ✅ Advantages |
|---|
| Preserves document structure |
| Useful for structured documents |
| Works particularly well with documents containing headings |

---

## 4. Metadata

Every chunk carries:

```
source_filename
page_number
chunk_index
section_heading
```

(DOCX chunks additionally carry `subsection_heading` since the hierarchical strategy has real `Heading 2` data to use.)

**Real example (from `native.pdf`, recursive strategy):**

```json
{
  "text": "CHAPTER 1\nIt is a truth universally acknowledged, that a single man in possession of a good fortune, must be in\nwant of a wife...",
  "metadata": {
    "source_filename": "native.pdf",
    "page_number": 2,
    "chunk_index": 1,
    "section_heading": "Unknown"
  }
}
```

### Metadata Verification

Verified across all three document types using the Recursive strategy as the representative production pass:

| Document | Chunks | Missing `source_filename` | Result |
|---|---|---|---|
| PDF | 478 | 0 | ✅ PASS |
| DOCX | 566 | 0 | ✅ PASS |
| TXT | 557 | 0 | ✅ PASS |

No chunk lost its source filename, across 1,601 total chunks generated in this run.

---

## 5. Chunk Size Trade-offs

### Smaller chunks

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| More focused retrieval | Less context |
| Less irrelevant information | More chunks |
| Better precision for specific questions | More retrieval operations |

### Larger chunks

| ✅ Advantages | ❌ Disadvantages |
|---|---|
| More surrounding context | May contain irrelevant information |
| Fewer chunks | Can reduce retrieval precision |
| Better for questions requiring broader context | Uses more model context |

The measured data above illustrates this directly: fixed-size at 500 chars produced 446–466 chunks per document, while the (much smaller, sentence-bounded) semantic chunks produced 828–867 — nearly double the chunk count for the same source text.

---

## 6. Overlap Trade-offs

Overlap helps preserve information near chunk boundaries.

- **Too little overlap** can cause context to be lost across a boundary.
- **Too much overlap** creates duplicate information, more chunks, and higher storage/retrieval cost.

> A moderate overlap such as **10–20%** (this build used 50/500 = 10% for fixed-size and 20/200 = 10% for token-based) is a reasonable starting point, but the best value depends on the document and retrieval task.

---

## 7. When Semantic Chunking Beats Fixed-size

**Semantic chunking** is preferable when:
- Documents contain clear topic changes
- Paragraphs contain strongly related information
- Maintaining semantic context is important

**Fixed-size chunking** is preferable when:
- Speed is important
- Documents are simple
- Predictable chunk sizes are required
- A baseline implementation is needed

In this run, semantic chunking was ~50x slower than fixed-size/recursive/hierarchical (0.5s vs ~0.00s per document) because it requires vectorizing every sentence — a real, measured cost of the "understands topic boundaries" benefit.

---

## 8. Conclusion

This build supports PDF (native + OCR), DOCX, and TXT ingestion; generates chunks via five distinct strategies; and attaches verified source metadata to every chunk — 1,601 chunks produced and metadata-checked with zero integrity failures across all three document types.

### Two things worth knowing if you run this elsewhere
1. **Token-based chunking** uses a regex tokenizer instead of `tiktoken` because this sandbox can't reach `openaipublic.blob.core.windows.net`. Swap in real `tiktoken` for exact GPT token counts.
2. **Semantic chunking** uses TF-IDF + cosine similarity instead of `sentence-transformers` because this sandbox can't reach `huggingface.co`. Swap in a real embedding model for higher-quality topic-boundary detection.

Both swaps are one-line changes in `src/chunking.py` (see the `NOTE:` comments in that file) — the chunking *logic* (embed → measure similarity/window → cut) is unchanged either way.

---

## Project Structure

```
day16_project/
├── data/                       # generated source documents
│   ├── native.pdf               (56 pages, real text layer)
│   ├── document.docx             (706 paragraphs, real heading styles)
│   ├── document.txt
│   └── scanned.pdf               (5 pages, image-only, for OCR)
├── src/
│   ├── generate_documents.py    # builds the 4 source files above
│   ├── ingestion.py              # PDFPlumber / PyPDF2 / python-docx / TXT
│   ├── ocr_pipeline.py           # pytesseract OCR + native-vs-OCR comparison
│   ├── chunking.py               # all 5 chunking strategies
│   └── run_pipeline.py           # runs everything, verifies metadata, saves output/
└── output/
    ├── pipeline_results.json     # every number in this README, machine-readable
    ├── ocr_comparison.txt
    └── chunks/                   # sample tagged chunks per strategy/document
```

To reproduce: `python3 src/generate_documents.py && python3 src/run_pipeline.py && python3 src/ocr_pipeline.py`
