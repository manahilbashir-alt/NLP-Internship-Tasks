# Classical NLP vs. Embeddings vs. Direct LLM Prompting

Three very different ways to get a computer to deal with text, and picking the wrong one is usually what makes a project either too slow, too expensive, or too brittle. Here's how I think about the tradeoffs.

## What each one actually is

**Classical NLP** is the old-school toolkit: regex, POS tagging, TF-IDF, CRFs, spaCy-style pipelines. You write rules or train small statistical models on labeled data, and the system does exactly what you told it to, nothing more. It's fast because there's no neural network doing the heavy lifting — just pattern matching and counting.

**Embeddings** turn text into vectors and let you compare things by meaning instead of exact wording. You embed a corpus once, then do similarity search (cosine distance, ANN indexes like FAISS or HNSW) to find what's related. It doesn't "understand" anything in a deep sense, but it's very good at telling you that "car" and "automobile" are close, even though a regex would call them totally different strings.

**Direct LLM prompting** just hands the raw text to a generative model and asks it to reason about it. No pipeline, no index — just a prompt. It's the most flexible option by a wide margin, and also the most expensive and least predictable.

## The tradeoffs, roughly

| | Classical NLP | Embeddings | LLM Prompting |
|---|---|---|---|
| Setup effort | Medium — feature engineering, pipeline config | Medium — pick a model, stand up a vector store | Low — write a prompt |
| Cost per query | Basically free, runs on CPU | Cheap — one encode plus a lookup | Real money, especially at scale |
| Speed | Milliseconds | Tens of milliseconds | Often a second or more |
| Can you explain a decision? | Yes, every step is visible | Sort of — you get a distance score, not a reason | Not really, unless you ask it to show its work |
| Needs labeled data? | Often yes | No — just a corpus to index | No |
| Deterministic? | Completely | Yes, given a fixed index | No, same input can give different output |
| Handles phrasing it's never seen | Poorly | Pretty well | Very well |
| Good at pulling exact fields or spans out of text | Yes, this is its strength | Not really on its own | Decent, but you should validate the output |
| Scales to huge volume | Great | Great | Gets expensive fast |

## When I'd reach for each one

Go **classical** when you need speed and you need to be able to explain why the system did what it did — think regulated industries, high-volume pipelines processing millions of documents a day, or narrow well-defined tasks like PII redaction where the patterns are known in advance. If the problem is boring and well-specified, don't overbuild it with a neural net.

Go **embeddings** when the task is fundamentally about finding things that mean the same thing rather than matching exact strings — semantic search, deduplication, clustering, recommendations, or as the retrieval layer in a RAG system. It's the sweet spot when you want semantic understanding at scale without paying LLM prices on every single query, and you don't need any labeled data to get started.

Go **straight to an LLM prompt** when the task is genuinely open-ended: multi-step reasoning, summarization, handling inputs you can't fully anticipate, or generalizing to new categories on the fly. It's also often the right call when the alternative is writing and maintaining a pile of custom logic to catch every edge case — sometimes paying for flexibility is cheaper than paying an engineer to maintain brittle rules.

## In practice

Most systems I've seen that work well don't pick just one. A typical pattern: classical NLP does cheap upfront filtering and structured extraction, embeddings narrow a huge set down to a relevant handful, and the LLM only gets called on that small, already-filtered set to do the actual reasoning or generation. That keeps the expensive step small and reserves the flexible tool for where flexibility actually earns its cost.
