\# Day 17 — Vector Database \& Embedding Benchmark



\## Overview



This project benchmarks different text embedding models and vector stores for a Retrieval-Augmented Generation (RAG) workflow.



The experiments evaluate:



\- Embedding model speed

\- Embedding dimensions

\- Retrieval quality

\- ChromaDB vs FAISS query speed

\- Collection management

\- Top-3 retrieval precision

\- Precision-to-speed trade-offs



The experiments use a collection of chunks extracted from \*Pride and Prejudice\* by Jane Austen.



\---



\# Project Objectives



The main objectives were:



1\. Compare multiple embedding models.

2\. Benchmark embedding generation speed.

3\. Configure ChromaDB.

4\. Configure FAISS.

5\. Compare vector search speed.

6\. Implement collection management utilities.

7\. Run a 20-question retrieval benchmark.

8\. Measure Top-3 precision.

9\. Determine the best precision-to-speed combination.



\---



\# Embedding Models



The following local embedding models were benchmarked:



| Model | Dimensions | Embedding Speed | Retrieval Precision |

|---|---:|---:|---:|

| all-MiniLM-L6-v2 | 384 | Fastest | 68.33% |

| all-mpnet-base-v2 | 768 | Medium | 75.00% |

| BAAI/bge-large-en-v1.5 | 1024 | Slowest | 80.00% |



\### Embedding generation benchmark



The initial benchmark used 494 document chunks.



| Model | Chunks | Dimensions | Load Time (s) | Embedding Time (s) | Chunks/sec |

|---|---:|---:|---:|---:|---:|

| all-MiniLM-L6-v2 | 494 | 384 | 6.565 | 11.555 | 42.75 |

| all-mpnet-base-v2 | 494 | 768 | 338.668 | 94.841 | 5.21 |

| BAAI/bge-large-en-v1.5 | 494 | 1024 | 852.977 | 307.984 | 1.60 |



\---



\# Retrieval Benchmark



A benchmark containing 20 factual questions was created.



For each question:



1\. The question was embedded.

2\. Cosine similarity was calculated against all document chunks.

3\. The top 3 chunks were retrieved.

4\. Retrieved chunks were evaluated for keyword-based relevance.

5\. Top-3 precision was calculated.



\## Results



| Model | Top-3 Precision | Average Query Time |

|---|---:|---:|

| all-MiniLM-L6-v2 | 68.33% | 11.99 ms |

| all-mpnet-base-v2 | 75.00% | 53.75 ms |

| BAAI/bge-large-en-v1.5 | 80.00% | 157.29 ms |



\### Interpretation



BGE-large achieved the highest retrieval precision at approximately 80%.



MPNet achieved 75% precision while requiring substantially less query time than BGE-large.



MiniLM was the fastest embedding model but produced the lowest retrieval precision among the three local models.



This demonstrates a clear trade-off between retrieval quality and computational cost.



\---



\# ChromaDB vs FAISS



A benchmark dataset containing 1,200 chunks was used to compare vector search performance.



\## Results



| Vector Store | Average Query Time |

|---|---:|

| ChromaDB | 1.2377 ms |

| FAISS | 0.1179 ms |



FAISS was approximately 10.5× faster than ChromaDB for raw vector search in this experiment.



\### ChromaDB



Advantages:



\- Persistent vector database

\- Collections

\- Metadata support

\- Easy document management

\- Incremental updates

\- Convenient for RAG applications



\### FAISS



Advantages:



\- Extremely fast similarity search

\- Efficient in-memory vector indexing

\- Simple API

\- Excellent for high-performance retrieval



FAISS is primarily a vector search library, whereas ChromaDB provides a more complete database-oriented experience.



\---



\# Collection Management



A ChromaDB management utility was implemented with support for:



\- Listing collections

\- Counting documents

\- Creating collections

\- Incrementally adding documents

\- Deleting collections



Implementation:



```text

src/vectorstores/chroma\_manager.py

