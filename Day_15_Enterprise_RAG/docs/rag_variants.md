# RAG Variants

## Overview

RAG (Retrieval-Augmented Generation) has evolved from a simple
retrieve-and-generate architecture into more advanced and modular systems.

The four important RAG variants studied in this project are:

1. Naive RAG
2. Advanced RAG
3. Modular RAG
4. GraphRAG

Each approach adds capabilities to address limitations of the previous
approach.

---

# 1. Naive RAG

## Definition

Naive RAG is the simplest form of Retrieval-Augmented Generation.

The system retrieves relevant documents or chunks and places them directly
into the prompt given to the LLM.

## Pipeline

```text
Documents
    |
    v
Chunking
    |
    v
Embeddings
    |
    v
Vector Database
    |
    v
Similarity Search
    |
    v
Retrieved Context
    |
    v
LLM
    |
    v
Answer
Main Components
Document ingestion
Chunking
Embedding
Vector store
Similarity retrieval
Prompt construction
LLM generation
Advantages
Simple to implement.
Easy to understand.
Fast to develop.
Works well for straightforward question answering.
Good starting point for RAG systems.
Limitations

Naive RAG can suffer from:

Poor chunking
Irrelevant retrieval
Missing information
Too much retrieved context
Duplicate information
Hallucination
Weak query understanding
Example

A user asks:

What is the annual refund period?

The system performs vector search, retrieves the relevant refund-policy
chunks, puts them into the prompt, and asks the LLM to answer.

2. Advanced RAG
Definition

Advanced RAG improves the basic retrieve-and-generate pipeline by adding
better retrieval and context-processing techniques.

Instead of simply retrieving chunks and immediately sending them to the LLM,
Advanced RAG attempts to improve the quality of the retrieved evidence.

Typical Pipeline
Query
  |
  v
Query Processing
  |
  v
Hybrid Retrieval
  |
  v
Candidate Documents
  |
  v
Reranking
  |
  v
Context Filtering
  |
  v
LLM
  |
  v
Grounded Answer
What Advanced RAG Adds
1. Hybrid Retrieval

Combines multiple retrieval strategies.

For example:

Vector Search + BM25 Keyword Search

Semantic search finds conceptually similar text, while BM25 can find exact
keywords and terminology.

2. Reranking

Instead of directly using the first retrieved results, the system can
retrieve a larger candidate set and then rerank those results.

Example:

Retrieve 20 candidates
        |
        v
     Reranker
        |
        v
Keep best 5

This can improve retrieval precision.

3. Query Expansion

The original question can be transformed into additional search queries.

Example:

Original:
"What is the refund period?"

Expanded queries:
"refund window"
"refund eligibility"
"how many days for a refund"
4. Context Compression

Irrelevant parts of retrieved documents can be removed before sending
the context to the LLM.

This reduces context size and helps the model focus on useful information.

5. Metadata Filtering

Documents can be filtered using metadata.

Example:

department = "HR"
document_type = "policy"
year = 2026

This prevents unrelated documents from entering the retrieval results.

Advantages
Better retrieval quality.
Better precision.
Better context utilization.
Lower chance of irrelevant information reaching the LLM.
More suitable for production systems.
Limitations
More complex architecture.
Additional processing.
More components to monitor.
Potentially higher latency.
3. Modular RAG
Definition

Modular RAG treats RAG as a collection of independent components or
modules rather than one fixed pipeline.

Each module can be replaced, improved, or independently configured.

Architecture
                    +----------------+
                    | Query Module   |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Retrieval      |
                    | Module         |
                    +-------+--------+
                            |
                +-----------+-----------+
                |                       |
                v                       v
        Vector Retrieval         Keyword Retrieval
                |                       |
                +-----------+-----------+
                            |
                            v
                    +----------------+
                    | Reranking      |
                    | Module         |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Context        |
                    | Processing     |
                    +-------+--------+
                            |
                            v
                    +----------------+
                    | Generation     |
                    | Module         |
                    +----------------+
What Modular RAG Adds

Modular RAG makes individual parts independently configurable.

Examples:

Retrieval Module

Can use:

Vector search
BM25
Hybrid retrieval
External search
Reranking Module

Can use:

Cross-encoder reranker
LLM-based reranking
Score-based reranking
Generation Module

Can use:

Gemini
GPT
Claude
Local LLM
Query Module

Can perform:

Query rewriting
Query expansion
Intent detection
Multi-query generation
Advantages
Highly flexible.
Easier to experiment with different components.
Easier to replace individual technologies.
Suitable for complex enterprise applications.
Components can be independently tested.
Limitations
More engineering complexity.
More configuration.
More components can introduce additional failure points.
4. GraphRAG
Definition

GraphRAG combines retrieval-augmented generation with a knowledge graph.

Instead of representing knowledge only as independent text chunks, the
system represents relationships between entities and concepts.

Traditional RAG

Traditional RAG mainly retrieves text passages.

Example:

Document
   |
   +-- Chunk 1
   +-- Chunk 2
   +-- Chunk 3

The chunks are mostly treated as independent retrieval units.

GraphRAG

GraphRAG represents entities and relationships.

Example:

Acme SaaS
    |
    | provides
    v
Annual Plan
    |
    | has refund window
    v
30 Days

Another example:

Employee
    |
    | works in
    v
Engineering
    |
    | manages
    v
Project A

The graph explicitly represents relationships between entities.

What GraphRAG Adds
1. Entity Extraction

The system identifies important entities from documents.

Examples:

People
Organizations
Products
Locations
Projects
Policies
2. Relationship Extraction

The system identifies relationships between entities.

Example:

Alice -> works_for -> Acme
Acme -> provides -> SaaS Platform
SaaS Platform -> has_policy -> Refund Policy
3. Graph-Based Retrieval

Instead of retrieving only textually similar chunks, the system can traverse
relationships in the graph.

This is especially useful when answering questions that require connecting
multiple pieces of information.

4. Multi-Hop Reasoning

GraphRAG can help with questions requiring multiple relationships.

Example:

Which department manages the project created by the company that acquired
Company X?

This type of question may require connecting multiple entities and
relationships.

Advantages
Good for relationship-heavy knowledge.
Supports multi-hop questions.
Makes relationships explicit.
Useful for complex enterprise knowledge.
Can organize large interconnected knowledge bases.
Limitations
More complex to build.
Requires graph construction.
Entity and relationship extraction can introduce errors.
More infrastructure may be required.
Often unnecessary for simple document question answering.
Comparison
Feature	Naive RAG	Advanced RAG	Modular RAG	GraphRAG
Basic retrieval	Yes	Yes	Yes	Yes
Vector search	Yes	Yes	Optional	Optional
Hybrid search	Usually no	Yes	Yes	Can be used
Reranking	Usually no	Yes	Yes	Can be used
Query rewriting	Usually no	Yes	Yes	Yes
Context compression	Usually no	Yes	Yes	Yes
Independent modules	Limited	Moderate	High	High
Knowledge graph	No	No	Optional	Yes
Relationship reasoning	Limited	Moderate	Depends on modules	Strong
Multi-hop questions	Limited	Better	Configurable	Strong
Complexity	Low	Medium	High	High
Best use case	Simple QA	Production RAG	Flexible enterprise systems	Relationship-heavy knowledge
Evolution of RAG

The progression can be understood as:

Naive RAG
    |
    | Adds better retrieval
    v
Advanced RAG
    |
    | Adds independent components
    v
Modular RAG
    |
    | Adds graph-based knowledge and relationships
    v
GraphRAG
Naive RAG

Focus:

Retrieve and generate.

Advanced RAG

Focus:

Retrieve better and provide better context.

Modular RAG

Focus:

Build RAG from replaceable and configurable components.

GraphRAG

Focus:

Retrieve and reason over relationships between entities.

When to Use Each Variant
Use Naive RAG When
The knowledge base is small.
Questions are simple.
A quick prototype is required.
Basic semantic retrieval is sufficient.
Use Advanced RAG When
Retrieval quality needs improvement.
Documents are large or complex.
Search needs both semantic and keyword matching.
Production-level accuracy is required.
Use Modular RAG When
Different retrieval strategies need to be tested.
The application has complex requirements.
Components need to be independently replaced.
The system is expected to evolve over time.
Use GraphRAG When
Relationships between entities are important.
Questions require multiple hops across information.
The knowledge base contains highly connected information.
Simple chunk retrieval is insufficient.
Key Takeaway

The variants do not simply represent four completely separate systems.

They represent different levels of capability and architectural complexity.

Naive RAG
Simple retrieval
     |
     v
Advanced RAG
Better retrieval + better context
     |
     v
Modular RAG
Replaceable and configurable components
     |
     v
GraphRAG
Knowledge relationships + graph-based retrieval

The correct architecture depends on the application's requirements.

A simple question-answering application may only need Naive RAG, while a
large enterprise knowledge system with complex relationships may benefit
from GraphRAG.