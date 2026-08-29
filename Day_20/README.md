# Day 20 – Advanced RAG with LangChain

## Overview

Day 20 focuses on building and experimenting with advanced Retrieval-Augmented Generation (RAG) techniques using LangChain.

The main goal of this task is to understand how LangChain retrievers can be used to retrieve relevant information from documents and how different retrieval strategies can improve the RAG pipeline.

This project implements multiple retriever approaches, including custom retrieval, compression-based retrieval, conversational RAG, and citation-based RAG.

---

## Objectives

The main objectives of Day 20 are:

- Understand LangChain retrievers.
- Build a LangChain-based retrieval pipeline.
- Implement a custom retriever.
- Implement contextual compression retrieval.
- Build a conversational RAG system.
- Add citations to retrieved information.
- Compare different retrieval approaches.
- Create tests to verify the implemented components.
- Expose the RAG functionality through an API.

---

## Technologies Used

- Python
- LangChain
- ChromaDB
- Sentence Transformers
- FastAPI
- Pytest
- Vector Search
- Retrieval-Augmented Generation (RAG)

---

## Project Structure

```text
Day_20/
│
├── data/
│   └── Documents used for retrieval
│
├── output/
│   └── Generated outputs and results
│
├── src/
│   ├── api.py
│   ├── citation_rag.py
│   ├── compare_retrievers.py
│   ├── compression_retriever.py
│   ├── conversation_rag.py
│   ├── custom_retriever.py
│   ├── evaluate_conversations.py
│   ├── langchain_retriever.py
│   │
│   ├── test_citations.py
│   ├── test_compression.py
│   ├── test_conversation.py
│   ├── test_custom.py
│   └── test_langchain.py
│
├── README.md
└── requirements.txt