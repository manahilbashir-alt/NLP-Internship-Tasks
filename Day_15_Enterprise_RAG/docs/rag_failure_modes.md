# RAG Failure Modes and Fixes

## 1. Poor Chunking

### Problem

If documents are split into chunks that are too large, too small, or in the
middle of important semantic sections, the retriever may not receive enough
useful context.

### Symptoms

- Answers contain incomplete information.
- Important information is split between chunks.
- Retrieval returns technically related but incomplete passages.

### Causes

- Fixed-size chunks without considering document structure.
- Very small chunks that lose context.
- Very large chunks that contain too much unrelated information.

### Fixes

- Use semantic or structure-aware chunking.
- Preserve headings and related paragraphs.
- Use chunk overlap.
- Experiment with chunk size and overlap.
- Keep metadata such as document name, page, and section.

### Recommended approach

Start with approximately 300-800 tokens per chunk and use a moderate overlap.
Adjust these values according to the document type and evaluation results.

---

## 2. Wrong Retrieval

### Problem

The retriever returns chunks that are not sufficiently relevant to the
user's question.

### Symptoms

- Correct information exists in the corpus but is not retrieved.
- Retrieved chunks contain related words but do not answer the question.
- The LLM produces an incorrect answer because the required context was
  missing.

### Causes

- Poor embeddings.
- Weak similarity search.
- Incorrect query formulation.
- Insufficient top-k results.
- Keyword-only retrieval missing semantic matches.

### Fixes

- Use strong embedding models.
- Combine semantic search with keyword/BM25 retrieval.
- Tune top-k.
- Use query expansion or rewriting.
- Add a reranking stage.
- Evaluate retrieval independently from generation.

### Recommended approach

Hybrid retrieval can combine dense vector similarity with lexical retrieval
such as BM25. A reranker can then reorder the retrieved candidates.

---

## 3. Context Overflow

### Problem

Too many retrieved chunks are passed to the LLM, causing excessive context
length or reducing the importance of the most relevant information.

### Symptoms

- Requests become slow or expensive.
- Important information gets buried in irrelevant context.
- The model may ignore useful information.
- The request may exceed the model's context limit.

### Causes

- Excessively high top-k.
- Large chunks.
- Duplicate retrieved content.
- No context compression.

### Fixes

- Reduce top-k.
- Use smaller, better chunks.
- Remove duplicate chunks.
- Apply reranking.
- Compress or summarize retrieved context.
- Set a maximum context/token budget.

### Recommended approach

Retrieve several candidates, rerank them, and pass only the highest-quality
chunks to the generation model.

---

## 4. Hallucination Despite Retrieval

### Problem

Relevant context is retrieved, but the LLM generates information that is
not supported by the retrieved documents.

### Symptoms

- The answer contains unsupported facts.
- The model adds information from its pretrained knowledge.
- The answer sounds confident even though the documents do not support it.

### Causes

- Weak grounding instructions.
- Retrieved context is ambiguous or incomplete.
- The model relies on prior knowledge.
- No verification step.
- No citation requirement.

### Fixes

- Explicitly instruct the model to use only retrieved context.
- Tell the model to say "I don't know" when evidence is insufficient.
- Require citations.
- Use a lower temperature when appropriate.
- Add an answer verification step.
- Evaluate faithfulness separately from answer relevance.

### Grounding prompt pattern

The generation prompt should clearly state:

1. Use only the provided context.
2. Do not use outside knowledge.
3. Do not guess.
4. If the answer is not supported, say so.
5. Cite the relevant source.

---

## Failure Prevention Summary

| Failure Mode | Main Fix |
|---|---|
| Poor chunking | Structure-aware chunking + overlap |
| Wrong retrieval | Hybrid retrieval + reranking |
| Context overflow | Top-k tuning + context compression |
| Hallucination | Strong grounding + citations + verification |

## Evaluation Strategy

RAG systems should evaluate both retrieval and generation.

Retrieval evaluation checks whether the correct information was retrieved.

Generation evaluation checks whether the final answer is relevant,
faithful, and supported by the retrieved context.