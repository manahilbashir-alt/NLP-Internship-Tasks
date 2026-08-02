# Smart Document Tagger

## Description

This project builds an end-to-end NLP pipeline that:

- Reads a raw text document
- Performs NLP preprocessing
- Extracts TF-IDF keywords
- Extracts embedding-based keywords
- Creates a few-shot prompt for an LLM
- Generates semantic document tags
- Saves the results as structured JSON

## Run

```bash
pip install -r requirements.txt

python smart_document_tagger.py
```