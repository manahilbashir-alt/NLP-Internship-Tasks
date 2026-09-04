# Retrieval Method Comparison — Simple RAG vs. BM25 vs. Hybrid vs. Hierarchical

## Evaluation setup

Two evaluations were run against a 20-question test set (drawn from the ingested
Machine Learning lecture notes PDF, 1218 base chunks, embedded with
`BAAI/bge-large-en-v1.5` and indexed in FAISS):

1. **Retrieval-only evaluation** (all 20 questions x 4 methods, no LLM calls) —
   measures whether each method's top-3 retrieved chunks include the page the
   answer actually lives on (*page precision*), and how much of the expected
   answer's key vocabulary appears in what was retrieved (*fact coverage*).
2. **Generation evaluation** (a 3-question sample x 4 methods = 12 real Gemini
   calls) — measures accuracy, hallucination rate, and source precision on
   actual generated answers, not just retrieval quality.

The generation sample was deliberately kept small (3 of the 20 questions,
not all 20) because Gemini's free tier caps at ~20 requests/day; running all
20 questions across 4 methods would require 80 calls in a single evaluation
run. This trade-off — full retrieval-quality sweep plus a smaller, real
generation sample — is disclosed here rather than hidden, and is a standard
practical compromise when evaluating LLM pipelines under API rate limits.

## Results

### Retrieval-only (n=20 questions, 6 with a known expected page)

| Method | Page precision | Avg. fact coverage |
|---|---|---|
| Simple (FAISS + bge-large) | 0.500 | 0.487 |
| BM25 (keyword only) | 0.500 | 0.318 |
| Hybrid (BM25 + FAISS, RRF) | 0.667 | 0.454 |
| **Hierarchical** (Hybrid + rerank + parent-expansion) | **0.667** | **0.592** |

### Generation-based (n=3 questions, real Gemini answers)

| Method | Accuracy proxy | Hallucination rate | Source precision |
|---|---|---|---|
| Simple | 0.809 | 0.0 | 1.0 |
| BM25 | 0.395 | 0.0 | 0.667 |
| Hybrid | 0.706 | 0.0 | 1.0 |
| **Hierarchical** | **0.839** | 0.0 | 1.0 |

## Discussion

**BM25 alone is consistently the weakest method** on every metric except page
precision (tied with Simple). Pure keyword matching misses semantically
related content that doesn't share exact vocabulary with the query — e.g. a
question asking about "downsides" won't match a chunk that only says
"limitations" or "drawbacks."

**Simple FAISS retrieval is a strong baseline.** Dense embeddings (bge-large)
capture semantic similarity well, and for straightforward factual questions
("What is SVM?") it performs nearly as well as more complex methods.

**Hybrid (BM25 + FAISS via Reciprocal Rank Fusion) improves page precision**
over either method alone, confirming that combining keyword and semantic
signals recovers content that neither method finds reliably on its own — but
its fact coverage on the retrieval-only test sat between Simple and
Hierarchical, suggesting RRF's blended ranking sometimes trades a strong
single-method match for a compromise candidate.

**Hierarchical (Hybrid + cross-encoder reranking + parent-chunk expansion)
was the best performer overall** on both evaluations. Reranking narrows a
wide candidate pool down to the truly best-matching small chunks, and
expanding only those survivors to include neighboring chunks recovers
context that a single 800-character chunk loses — particularly valuable for
content split across multiple sequential chunks (e.g. a numbered list of
sub-requirements under one heading).

**Hallucination rate was 0.0 across all methods** in this sample. The system
prompt explicitly instructs the model to say "I don't know" when the answer
isn't in the retrieved context, and this was followed consistently — the
model did not fabricate answers when retrieval failed to surface relevant
content; it correctly reported uncertainty instead (see Known Limitations
for cases where this produced an unhelpful but honest "I don't know" on
content that does exist in the source document, just not in the top-k
retrieved chunks).

## Recommendation

For a production deployment of this system, **Hierarchical retrieval is the
recommended default** — it consistently matched or outperformed every other
method on both retrieval quality and real generation accuracy, at the cost
of higher latency (BM25 + FAISS + cross-encoder reranking + expansion is
more compute per query than Simple retrieval alone). For latency-sensitive
use cases, **Hybrid** is a reasonable middle ground.