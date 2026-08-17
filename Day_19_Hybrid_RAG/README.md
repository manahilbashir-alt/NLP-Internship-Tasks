\# Day 19 — Hybrid RAG: BM25 + Vector Search + RRF



\## Overview



This project implements and evaluates a Hybrid Retrieval-Augmented Generation (RAG) search pipeline.



The system combines:



\- BM25 lexical retrieval

\- Dense vector retrieval using Sentence Transformers

\- ChromaDB for vector search

\- Reciprocal Rank Fusion (RRF) for combining retrieval rankings



The goal is to compare lexical search, semantic search, and hybrid retrieval on the same document collection.



\---



\## Project Structure



```text

Day\_19\_Hybrid\_RAG/

│

├── data/

│   ├── rag\_basics.txt

│   └── vector\_database\_notes.txt

│

├── src/

│   ├── hybrid\_search.py

│   └── benchmark\_hybrid.py

│

├── output/

│   ├── hybrid\_retrieval\_detailed.csv

│   └── hybrid\_retrieval\_summary.csv

│

└── README.md

Retrieval Pipeline



User Query

&#x20;    │

&#x20;    ├───────────────┐

&#x20;    ↓               ↓

&#x20;  BM25        Vector Search

&#x20;    │               │

&#x20;    └───────┬───────┘

&#x20;               ↓

&#x20;      Reciprocal Rank

&#x20;         Fusion

&#x20;            ↓

&#x20;     Hybrid Ranking

&#x20;            ↓

&#x20;      Top-K Results



1\. BM25 Retrieval



BM25 is a lexical retrieval algorithm that ranks documents based on the occurrence and importance of query terms.



It is useful for:



Exact keyword matching

Technical terminology

Queries where important words appear directly in documents



However, BM25 can struggle when the query uses different wording from the indexed document.



2\. Vector Retrieval



Dense vector retrieval uses:



sentence-transformers/all-MiniLM-L6-v2



Documents and queries are converted into dense embeddings.



ChromaDB is used to perform similarity search over these embeddings.



Vector retrieval is useful for:



Semantic similarity

Different wording

Conceptually related queries

3\. Reciprocal Rank Fusion



The system combines BM25 and vector rankings using Reciprocal Rank Fusion (RRF).



The formula used is:



RRF(d) = Σ 1 / (k + rank(d))



where:



k = 60



A document appearing in both retrieval systems receives a higher combined ranking.



4\. Benchmark



A benchmark containing 10 factual questions was created.



For every question, the system calculates Top-3 precision for:



BM25

Vector Search

Hybrid RRF

Results

Method	Average Top-3 Precision

BM25	70.00%

Vector Search	73.33%

Hybrid RRF	76.67%

Result



Hybrid RRF achieved the highest precision on the benchmark.



Compared with BM25:



76.67% - 70.00% = 6.67 percentage points



Compared with vector search:



76.67% - 73.33% = 3.34 percentage points



Therefore, on this document collection and benchmark, combining lexical and semantic retrieval produced the best Top-3 precision.



5\. Example Query



Example:



What are the advantages of vector databases?



The system independently generates:



BM25 Results

&#x20;     ↓

Vector Results

&#x20;     ↓

RRF Fusion

&#x20;     ↓

Hybrid Results



This allows lexical and semantic retrieval signals to complement each other.



6\. Limitations



This benchmark is relatively small:



2 source documents

10 chunks

10 evaluation questions



Therefore, the results should be interpreted as findings for this particular document set rather than as a universal comparison of retrieval methods.



A larger benchmark with more documents and manually validated relevance labels would provide stronger evidence.



7\. How to Run



From the project root:



python -m Day\_19\_Hybrid\_RAG.src.hybrid\_search



The interactive system accepts questions and displays:



BM25 results

Vector search results

Hybrid RRF results



To run the benchmark:



python -m Day\_19\_Hybrid\_RAG.src.benchmark\_hybrid



The benchmark outputs:



output/hybrid\_retrieval\_detailed.csv

output/hybrid\_retrieval\_summary.csv

Technologies

Python

BM25

Rank-BM25

Sentence Transformers

all-MiniLM-L6-v2

ChromaDB

Reciprocal Rank Fusion (RRF)

Conclusion



The experiment demonstrates the benefit of hybrid retrieval.



For this dataset:



BM25        → 70.00%

Vector      → 73.33%

Hybrid RRF  → 76.67%



Hybrid RRF achieved the best Top-3 precision by combining lexical and semantic retrieval signals.

