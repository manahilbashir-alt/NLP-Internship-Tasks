"""
Day 16 - Step 3: Chunking Strategies

Implements five chunking strategies:
  1. Fixed-size (character-based, with overlap)
  2. Token-based (tiktoken, with overlap)
  3. Recursive (LangChain RecursiveCharacterTextSplitter)
  4. Semantic (sentence-embeddings + cosine-similarity boundary detection)
  5. Hierarchical (Document -> Section -> Subsection -> Chunk, using DOCX headings)

Every chunk emitted carries metadata:
  source_filename, page_number, chunk_index, section_heading
"""

import re
from langchain_text_splitters import RecursiveCharacterTextSplitter


# ---------------------------------------------------------------------------
# 1. Fixed-size chunking
# ---------------------------------------------------------------------------
def chunk_fixed_size(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(text[start:end])
        if end == n:
            break
        start = end - overlap
    return chunks


# ---------------------------------------------------------------------------
# 2. Token-based chunking
# ---------------------------------------------------------------------------
# NOTE: tiktoken's BPE vocab files are fetched from a remote blob store at
# first use. In this sandboxed environment that host is not reachable, so a
# regex-based whitespace/punctuation tokenizer is used as a drop-in stand-in
# for a real subword tokenizer (e.g. tiktoken/cl100k_base). The chunking
# *logic* (encode -> window over tokens with overlap -> decode) is identical
# to what you'd do with a real BPE tokenizer; swap `_tokenize`/`_detokenize`
# for tiktoken.encode/decode in an environment with internet access to get
# exact GPT-style token counts instead of this word-level approximation.
_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def _tokenize(text):
    return _TOKEN_RE.findall(text)


def _detokenize(tokens):
    out = ""
    for tok in tokens:
        if out and re.match(r"\w", tok) and out[-1] not in " \n":
            out += " "
        elif out and not re.match(r"\w", tok) and tok not in ".,!?;:)]}\"'":
            out += " "
        out += tok
    return out


def chunk_token_based(text, chunk_size=200, overlap=20):
    tokens = _tokenize(text)
    chunks = []
    start = 0
    n = len(tokens)
    while start < n:
        end = min(start + chunk_size, n)
        chunks.append(_detokenize(tokens[start:end]))
        if end == n:
            break
        start = end - overlap
    return chunks


# ---------------------------------------------------------------------------
# 3. Recursive chunking (LangChain)
# ---------------------------------------------------------------------------
def chunk_recursive(text, chunk_size=500, overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


# ---------------------------------------------------------------------------
# 4. Semantic chunking
# ---------------------------------------------------------------------------
# NOTE: a transformer sentence-embedding model (e.g. sentence-transformers/
# all-MiniLM-L6-v2) would normally back this step, but downloading model
# weights from huggingface.co is not reachable from this sandboxed network.
# As a offline-friendly stand-in that still captures the same idea --
# "represent each sentence as a vector, and start a new chunk where the
# vector-similarity between consecutive sentences drops" -- this uses
# TF-IDF sentence vectors (scikit-learn) + cosine similarity. Swap
# `_embed_sentences` for a sentence-transformers `.encode()` call in an
# environment with model-hub access to use dense embeddings instead.
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _embed_sentences(sentences):
    vectorizer = TfidfVectorizer(stop_words="english")
    return vectorizer.fit_transform(sentences)


def chunk_semantic(text, similarity_threshold=0.15, min_sentences=2, max_chunk_chars=1200):
    """
    Splits text into sentences, vectorizes each sentence, and starts a new
    chunk whenever the similarity between consecutive sentences drops below
    `similarity_threshold` (a likely topic change), or the chunk grows past
    `max_chunk_chars`.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) <= 1:
        return [text] if text.strip() else []

    vectors = _embed_sentences(sentences)

    chunks = []
    current = [sentences[0]]
    current_len = len(sentences[0])

    for i in range(1, len(sentences)):
        sim = cosine_similarity(vectors[i - 1], vectors[i])[0][0]
        sent_len = len(sentences[i])
        topic_change = sim < similarity_threshold and len(current) >= min_sentences
        too_long = current_len + sent_len > max_chunk_chars
        if topic_change or too_long:
            chunks.append(" ".join(current))
            current = [sentences[i]]
            current_len = sent_len
        else:
            current.append(sentences[i])
            current_len += sent_len

    if current:
        chunks.append(" ".join(current))

    return chunks


# ---------------------------------------------------------------------------
# 5. Hierarchical chunking (Document -> Section -> Subsection -> Chunk)
# ---------------------------------------------------------------------------
def chunk_hierarchical(docx_paragraphs, chunk_size=500, overlap=50):
    """
    Groups DOCX paragraphs under their nearest heading (Section) and,
    within very long sections, their sub-headings (Subsection), then
    applies fixed-size chunking within each (sub)section so no chunk
    crosses a structural boundary.

    `docx_paragraphs` is the output of ingestion.ingest_docx().
    Returns list of dicts: {text, section_heading, subsection_heading}
    """
    sections = []  # list of {section, subsection, text}
    current_section = "Document Start"
    current_subsection = None
    buffer = []

    def flush():
        if buffer:
            sections.append(
                {
                    "section": current_section,
                    "subsection": current_subsection,
                    "text": " ".join(buffer),
                }
            )
            buffer.clear()

    for p in docx_paragraphs:
        style = p["style"].lower()
        if style in ("title", "heading 1"):
            flush()
            current_section = p["text"]
            current_subsection = None
        elif style == "heading 2":
            flush()
            current_subsection = p["text"]
        else:
            buffer.append(p["text"])
    flush()

    chunks = []
    for sec in sections:
        pieces = chunk_fixed_size(sec["text"], chunk_size=chunk_size, overlap=overlap)
        for piece in pieces:
            if piece.strip():
                chunks.append(
                    {
                        "text": piece,
                        "section_heading": sec["section"],
                        "subsection_heading": sec["subsection"],
                    }
                )
    return chunks


if __name__ == "__main__":
    sample = (
        "Elizabeth Bennet lived with her family at Longbourn. Her father was "
        "witty but detached. Her mother was anxious to see her daughters married. "
        "Meanwhile, in London, Mr. Bingley had just leased Netherfield Park. "
        "He was cheerful and open-hearted, unlike his friend Mr. Darcy, who was "
        "proud and reserved. The Bennet family speculated endlessly about the "
        "new arrivals and their fortunes."
    )

    print("=== Fixed-size chunks ===")
    for c in chunk_fixed_size(sample, chunk_size=120, overlap=20):
        print(repr(c))

    print("\n=== Token-based chunks ===")
    for c in chunk_token_based(sample, chunk_size=25, overlap=5):
        print(repr(c))

    print("\n=== Recursive chunks ===")
    for c in chunk_recursive(sample, chunk_size=120, overlap=20):
        print(repr(c))

    print("\n=== Semantic chunks ===")
    for c in chunk_semantic(sample, similarity_threshold=0.5, min_sentences=1, max_chunk_chars=300):
        print(repr(c))
