\# Day 18 - Simple RAG Retrieval and Generation



\## Objective



Implement a complete Retrieval-Augmented Generation (RAG) pipeline using

vector similarity retrieval, ChromaDB, embeddings, an augmented prompt,

and an LLM.



\---



\## RAG Pipeline



```text

User Question

&#x20;     ↓

Query Embedding

&#x20;     ↓

ChromaDB Similarity Search

&#x20;     ↓

Top-K Retrieved Chunks

&#x20;     ↓

Augmented Prompt

&#x20;     ↓

Gemini LLM

&#x20;     ↓

Grounded Answer

&#x20;     ↓

Source References



\## Features

Sentence Transformer embeddings

ChromaDB vector database

Top-k similarity retrieval

Similarity scores

Source metadata

Augmented prompt construction

Grounded LLM responses

Source references

Interactive CLI

Multiple document retrieval

No-answer handling

RAG failure analysis



\## Project Structure



Day\_18\_RAG\_Retrieval\_Generation/

│

├── data/

│   ├── documents/

│   │   ├── rag\_basics.txt

│   │   └── vector\_database\_notes.txt

│   │

│   └── chroma\_db/

│

├── docs/

│   └── simple\_rag\_failure\_analysis.md

│

├── src/

│   ├── \_\_init\_\_.py

│   ├── retrieval.py

│   ├── prompt.py

│   ├── generator.py

│   └── rag\_cli.py

│

├── tests/

│

├── .env

├── requirements.txt

└── README.md



