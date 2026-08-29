# Day 20 - Conversational RAG Evaluation

## Objective

Test 10 multi-turn conversations and document where session memory helps retrieval quality and where it introduces noise.

## Summary

- Total conversations: 10
- Total turns: 30
- Memory helped: 12
- Possible memory noise: 0
- Neutral: 8
- Baseline turns: 10

## Conversation Results

### Conversation 1: ChromaDB

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | What is ChromaDB? | What is ChromaDB? | baseline | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 2 | What about the second point? | Regarding the previous question 'What is ChromaDB?', the user now asks: What about the second point? | helped | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 3 | Why is it useful in RAG? | Regarding the previous question 'What about the second point?', the user now asks: Why is it useful in RAG? | helped | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |

### Conversation 2: Embeddings

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | What are embeddings? | What are embeddings? | baseline | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 2 | How are they used in retrieval? | Regarding the previous question 'What are embeddings?', the user now asks: How are they used in retrieval? | helped | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 3 | What about the previous concept? | Regarding the previous question 'How are they used in retrieval?', the user now asks: What about the previous concept? | helped | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |

### Conversation 3: Vector databases

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | What is a vector database? | What is a vector database? | baseline | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |
| 2 | How does it help RAG? | Regarding the previous question 'What is a vector database?', the user now asks: How does it help RAG? | helped | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 3 | What about similarity search? | Regarding the previous question 'How does it help RAG?', the user now asks: What about similarity search? | helped | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |

### Conversation 4: Similarity search

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | What is similarity search? | What is similarity search? | baseline | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 2 | What does it compare? | Regarding the previous question 'What is similarity search?', the user now asks: What does it compare? | helped | rag_basics.txt (Page 1) |
| 3 | Why is that important? | Regarding the previous question 'What does it compare?', the user now asks: Why is that important? | helped | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |

### Conversation 5: RAG

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | What is RAG? | What is RAG? | baseline | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 2 | What is the retrieval part? | What is the retrieval part? | neutral | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |
| 3 | What happens after retrieval? | What happens after retrieval? | neutral | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |

### Conversation 6: Embeddings and queries

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | How is a user question converted for retrieval? | How is a user question converted for retrieval? | baseline | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 2 | What is compared with it? | What is compared with it? | neutral | rag_basics.txt (Page 1) |
| 3 | Why are embeddings needed? | Regarding the previous question 'What is compared with it?', the user now asks: Why are embeddings needed? | helped | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |

### Conversation 7: Vector retrieval

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | How does vector retrieval work? | How does vector retrieval work? | baseline | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |
| 2 | What happens to the query? | What happens to the query? | neutral | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 3 | What about the stored documents? | Regarding the previous question 'What happens to the query?', the user now asks: What about the stored documents? | helped | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |

### Conversation 8: ChromaDB and RAG

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | How can ChromaDB be used in RAG? | How can ChromaDB be used in RAG? | baseline | rag_basics.txt (Page 1) |
| 2 | What does it store? | Regarding the previous question 'How can ChromaDB be used in RAG?', the user now asks: What does it store? | helped | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 3 | How does retrieval happen? | How does retrieval happen? | neutral | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |

### Conversation 9: Document chunks

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | Why do RAG systems use document chunks? | Why do RAG systems use document chunks? | baseline | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |
| 2 | How are chunks retrieved? | How are chunks retrieved? | neutral | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |
| 3 | What about embeddings? | Regarding the previous question 'How are chunks retrieved?', the user now asks: What about embeddings? | helped | vector_database_notes.txt (Page 1); rag_basics.txt (Page 1) |

### Conversation 10: Independent question after context

| Turn | Question | Contextualized Question | Memory Effect | Sources |
|---|---|---|---|---|
| 1 | What is ChromaDB? | What is ChromaDB? | baseline | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 2 | What is similarity search? | What is similarity search? | neutral | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |
| 3 | Tell me about embeddings. | Tell me about embeddings. | neutral | rag_basics.txt (Page 1); vector_database_notes.txt (Page 1) |

## Findings

### Where session memory helps

- Follow-up questions such as "What about the second point?" can be contextualized using the previous user question.
- Pronoun-based questions such as "Why is it useful?" can retain the previous conversational topic.
- Session history allows retrieval to receive a more complete query instead of an ambiguous follow-up.

### Where session memory can introduce noise

- Independent questions may not need previous conversation context.
- Automatically adding previous context to an independent question can make the retrieval query unnecessarily longer.
- Long conversation histories can eventually introduce unrelated information if memory is not managed.

## Conclusion

Session memory improves conversational RAG when the user asks follow-up questions that depend on previous turns. However, memory should be applied selectively because unrelated questions can introduce unnecessary context and retrieval noise.
