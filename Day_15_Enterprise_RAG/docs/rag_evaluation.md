# RAG Evaluation Metrics

## Overview

A RAG system should not be evaluated only by checking whether the final
answer looks correct.

A reliable RAG system must be evaluated at different stages of the
pipeline:

```text
Query
  |
  v
Retrieval
  |
  v
Retrieved Context
  |
  v
LLM Generation
  |
  v
Final Answer
Four important RAG evaluation metrics are:

Faithfulness
Answer Relevance
Context Precision
Context Recall

These metrics evaluate different parts of the RAG pipeline.

1. Faithfulness
Definition

Faithfulness measures whether the generated answer is supported by the
retrieved context.

In other words:

Does the answer contain claims that are actually supported by the
retrieved information?

A faithful answer should not introduce unsupported facts.

Example
Retrieved Context
Annual plans have a 30-day refund window from the date of purchase.
Faithful Answer
Annual plans can be refunded within 30 days of purchase.

The answer is supported by the retrieved context.

Therefore:

Faithfulness = High
Unfaithful Answer
Annual plans can be refunded within 60 days of purchase.

The retrieved context says 30 days, not 60 days.

Therefore:

Faithfulness = Low
What It Detects

Faithfulness helps detect:

Hallucinations
Unsupported claims
Incorrect generated facts
Information added from the model's prior knowledge
How to Improve Faithfulness
Use strong grounding instructions.
Tell the model to use only retrieved context.
Require source citations.
Improve retrieval quality.
Use lower temperature for factual QA.
Add answer verification.
Allow the model to abstain when evidence is missing.
2. Answer Relevance
Definition

Answer Relevance measures whether the generated answer actually addresses
the user's question.

A response can be factually correct but still fail to answer the question
directly.

Example
Question
What is the annual refund period?
Relevant Answer
The annual refund period is 30 days from the date of purchase.

This directly answers the question.

Therefore:

Answer Relevance = High
Irrelevant Answer
Customers can contact the billing department by email. Refunds are usually
reviewed within two business days.

This information may exist in the documents, but it does not directly answer
the question about the refund period.

Therefore:

Answer Relevance = Low
What It Detects

Answer Relevance helps identify:

Off-topic answers
Overly verbose responses
Responses that avoid the question
Answers containing related but unnecessary information
How to Improve Answer Relevance
Improve query understanding.
Use query rewriting.
Retrieve question-specific chunks.
Use clear generation prompts.
Avoid unnecessarily large contexts.
Instruct the model to answer the exact question.
3. Context Precision
Definition

Context Precision measures how much of the retrieved context is relevant
to answering the user's question.

The goal is not simply to retrieve many documents.

The goal is to retrieve the right documents.

Example
Question
What is the annual refund period?

Suppose the retriever returns five chunks:

Chunk 1 -> Annual refund policy        Relevant
Chunk 2 -> Annual plan cancellation   Relevant
Chunk 3 -> Data retention policy      Irrelevant
Chunk 4 -> Enterprise contracts       Irrelevant
Chunk 5 -> Billing contact information Irrelevant

Only two of the five retrieved chunks are highly useful.

Therefore, context precision is relatively low.

Why It Matters

Low context precision means the LLM receives unnecessary information.

This can cause:

Confusion
Longer prompts
Higher token usage
Increased latency
Greater chance of incorrect answers
How to Improve Context Precision
Improve embeddings.
Use hybrid retrieval.
Tune similarity thresholds.
Use metadata filtering.
Add reranking.
Reduce unnecessary top-K results.
Improve chunking.
4. Context Recall
Definition

Context Recall measures whether the retrieval system successfully retrieved
the information needed to answer the question.

In simple terms:

Did we retrieve all the important evidence required for the answer?

Example

Suppose the answer requires two pieces of information:

1. Annual plans have a 30-day refund window.
2. After 30 days, annual plans are non-refundable.

If retrieval returns both pieces:

Context Recall = High

If retrieval only returns:

Annual plans have a 30-day refund window.

then an important part of the evidence is missing.

Therefore:

Context Recall = Lower
Why It Matters

Low context recall means the required information exists in the knowledge
base but the retrieval system failed to retrieve it.

The LLM cannot reliably use information it never received.

How to Improve Context Recall
Improve chunking.
Increase retrieval candidate size.
Improve embedding models.
Use hybrid retrieval.
Use query expansion.
Use multi-query retrieval.
Use reranking after retrieving a larger candidate set.
Preserve relationships between related chunks.
Precision vs Recall

These two metrics evaluate retrieval from different perspectives.

Context Precision

Asks:

Of the information we retrieved, how much was relevant?

High Precision
= Less irrelevant information
Context Recall

Asks:

Of the information we needed, how much did we retrieve?

High Recall
= Less missing information
Example

Suppose the knowledge base contains 100 chunks.

Only 5 are required to answer a question.

System A

Retrieves 5 chunks:

4 relevant
1 irrelevant

This has relatively good precision, but one relevant chunk may be missing.

System B

Retrieves 20 chunks:

5 relevant
15 irrelevant

This has high recall but lower precision.

The goal is to achieve a good balance between precision and recall.

Metric Comparison
Metric	Evaluates	Main Question	Failure Detected
Faithfulness	Generated answer	Is the answer supported by context?	Hallucination
Answer Relevance	Generated answer	Does the answer address the question?	Off-topic answer
Context Precision	Retrieved context	How much retrieved context is relevant?	Irrelevant retrieval
Context Recall	Retrieved context	Did retrieval find the required evidence?	Missing evidence
Relationship to the RAG Pipeline

The four metrics evaluate different stages.

                 RAG PIPELINE

Query
  |
  v
Retrieval
  |
  +----------------------+
  |                      |
  v                      v
Context Precision   Context Recall
  |
  v
Augmented Prompt
  |
  v
LLM
  |
  +----------------------+
  |                      |
  v                      v
Faithfulness       Answer Relevance
  |
  v
Final Answer
Diagnosing RAG Problems Using Metrics

Metrics can help identify where a RAG system is failing.

Case 1: Low Context Recall

The system is not retrieving enough relevant information.

Possible causes:

Poor embeddings
Poor chunking
Query mismatch
Retrieval parameters too strict
Fix

Improve retrieval and chunking.

Case 2: Low Context Precision

The system retrieves too much irrelevant information.

Possible causes:

Top-K is too high
Weak embeddings
Poor chunking
No reranking
Fix

Use reranking, metadata filtering, and better retrieval.

Case 3: High Context Recall + Low Faithfulness

The correct information was retrieved, but the model still produced an
unsupported answer.

Likely Problem

Generation/grounding problem.

Fix
Strengthen the prompt.
Require citations.
Lower temperature.
Add answer verification.
Case 4: High Faithfulness + Low Answer Relevance

The answer is supported by the documents but does not directly answer
the user's question.

Likely Problem

The generation step is not focused enough on the user's query.

Fix

Improve query understanding and generation instructions.

Evaluation Strategy

A production RAG system should evaluate both retrieval and generation.

A basic evaluation process can be:

1. Create representative questions.
          |
          v
2. Define expected evidence.
          |
          v
3. Run retrieval.
          |
          v
4. Evaluate context precision.
          |
          v
5. Evaluate context recall.
          |
          v
6. Generate answers.
          |
          v
7. Evaluate faithfulness.
          |
          v
8. Evaluate answer relevance.
Important Principle

A high-quality RAG system needs good retrieval and good generation.

For example:

Good Retrieval
      +
Good Grounding
      +
Relevant Answer
      =
Reliable RAG System

A powerful LLM cannot completely compensate for poor retrieval.

Similarly, perfect retrieval does not guarantee a faithful answer if the
LLM ignores the retrieved context.

Conclusion

The four core RAG evaluation metrics provide complementary information:

Faithfulness

Checks whether the generated answer is supported by retrieved context.

Answer Relevance

Checks whether the generated answer actually addresses the user's question.

Context Precision

Checks whether retrieved information is relevant.

Context Recall

Checks whether the required information was successfully retrieved.

Together, these metrics provide a more complete picture of RAG quality than
evaluating the final answer alone.