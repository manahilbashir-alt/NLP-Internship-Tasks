# enterprise_rag_engine

A working RAG pipeline scaffold — not just docs, the code in `src/` actually runs end to end against the sample doc in `data/corpus/`.

Read `docs/RAG_STUDY.md` first if you want the reasoning behind the choices here (chunking strategy, why hybrid retrieval, RAG vs fine-tuning, failure modes, RAG variants, eval metrics). This README is just how to run the thing.

## Quick start

```bash
pip install -r requirements.txt
PYTHONPATH=src python3 src/pipeline.py "your question here"
```

Drop your own PDFs/txt/md files into `data/corpus/` first — there's a sample refund-policy doc in there now just so the pipeline has something to chew on out of the box.

## Run the smoke tests

```bash
PYTHONPATH=src python3 tests/test_pipeline.py
```

## Layout

```
enterprise_rag_engine/
├── docs/RAG_STUDY.md      # design notes / research writeup
├── src/
│   ├── ingestion.py        # PDF/text parsing -> cleaned Document objects
│   ├── chunking.py         # recursive splitting + overlap
│   ├── embedding.py        # sentence-transformers wrapper
│   ├── vector_store.py     # chromadb persistence + query
│   ├── retrieval.py        # hybrid dense + BM25, fused with RRF
│   └── pipeline.py         # runs the whole chain, builds the final prompt
├── data/
│   ├── corpus/             # put your source documents here
│   ├── chunks/
│   └── vector_store/       # persisted chroma index (gitignore this in a real repo)
├── tests/test_pipeline.py
└── requirements.txt
```

## Note on the embedding model

`embedding.py` defaults to `all-MiniLM-L6-v2` via sentence-transformers. If it can't reach the model hub (e.g. an offline/sandboxed environment), it falls back to a deterministic hashing embedder — that fallback is bag-of-words only, good enough to prove the plumbing works, not good enough to actually use. In any environment with normal network access it'll use the real model without any code changes.
