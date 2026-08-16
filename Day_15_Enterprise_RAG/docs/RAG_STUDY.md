# RAG notes — enterprise_rag_engine

These are my working notes from putting this pipeline together, not a polished paper. Kept the tone practical since it's what I'll actually reread later. Code that backs this up lives in `src/` and runs end to end against the sample doc in `data/corpus/`.

---

## 1. What actually happens between a question and an answer

The pipeline, in order:

**Corpus → Ingestion → Chunking → Embedding → Vector store → Retrieval → Augmented prompt → LLM → Grounded response**

Worth saying up front: nothing downstream fixes a bad corpus. If the source docs are stale, duplicated, or contradictory, you can tune retrieval and reranking all day and the answers will still be wrong — they'll just be wrong *confidently*, with a citation attached. So corpus hygiene isn't step zero you skip past, it's the thing that determines the ceiling on everything else.

**Ingestion** is where you turn PDFs, docs, wikis, whatever, into text plus metadata. I used `pypdf` for the fast path and `pdfplumber` when tables need to survive (pypdf tends to smash table rows into unreadable strings). The annoying part of ingestion is never the happy path — it's the scanned PDF that needs OCR, the multi-column layout that reads left-then-right instead of top-to-bottom, the header/footer text that repeats on every page and pollutes every chunk. Capture metadata here too — source path, page number, section — because you can't bolt citations on later without it.

**Chunking** splits documents into pieces small enough to embed and retrieve sensibly. I went with recursive splitting: try paragraph breaks first, fall back to sentence breaks, fall back to a hard character cut only if something truly oversized shows up (a giant table row, say). Added ~15% overlap between chunks so a fact sitting right on a boundary doesn't get orphaned. Chunk size is a real trade-off and I don't think there's a universally correct number — I started around 500 characters for this project and would tune per corpus. Smaller chunks retrieve more precisely but carry less surrounding context; bigger chunks carry more context but dilute the embedding and eat more of the prompt budget.

**Embedding** turns text into vectors that capture meaning rather than exact wording, so "cancel my subscription" and "how do I terminate my plan" land near each other in vector space even though they share almost no words. Used `sentence-transformers` (`all-MiniLM-L6-v2` as the default, swappable for something bigger like `bge-large` if a domain needs it). One thing that bit me building this: whatever model embeds the corpus has to be the exact same model that embeds the query at search time, otherwise you're comparing vectors from two different spaces and the numbers are meaningless.

**Vector store** — `chromadb` here, persisted to disk under `data/vector_store/`. It's doing approximate nearest-neighbor search under the hood so it can find close vectors in a big index without brute-forcing a comparison against every single one. Also holds the original chunk text and metadata alongside the vector, since a bare vector is useless to return to a user — you need the text and source back.

**Retrieval** is where I spent the most time, because it's the step most likely to quietly wreck everything else. Went with hybrid: dense (vector) search plus BM25 keyword search, combined with reciprocal rank fusion. The reason for both — dense embeddings are great at "this means roughly the same thing" but genuinely bad at exact matches: product SKUs, error codes, acronyms, anything where the *exact string* matters. BM25 catches those. Fusing the two rankings beats picking one, in my experience and in most of what's published on this.

**Augmented prompt** — this is just string assembly, but the instructions matter more than people expect. The single highest-leverage line in the whole system, in my opinion, is telling the model explicitly to say it doesn't know when the context doesn't cover the question. Skip that line and models will confidently fill gaps from their own training data, which defeats the entire point of retrieving grounded context in the first place.

**LLM → grounded response** — the model reasons over what got handed to it and (ideally) cites which numbered chunk backed which claim. "Grounded" here specifically means: the factual content in the answer traces back to something retrieved, not to whatever the model happened to memorize during training.

---

## 2. RAG or fine-tuning — how I'd actually decide

People frame this as a versus, but they change different things. RAG changes what the model has *in front of it* at answer time. Fine-tuning changes the *weights* — how the model behaves, not what it knows in the moment. Once that clicks, the decision usually falls out on its own.

**Reach for RAG when:**

- The knowledge moves. Pricing, policy docs, ticket status, anything that changes weekly or daily. Update the index, done — no retraining loop.
- You need to show your work. Legal, medical, financial, compliance — anywhere someone will ask "where did that come from." RAG gives you a citation for free; a fine-tuned model just gives you an assertion.
- The knowledge base is huge and mostly irrelevant per query. Thousands of internal docs where any given question only needs three of them. Baking all of that into weights is expensive and mostly wasted.
- Different users need to see different data. Multi-tenant systems, customer-specific docs — RAG can filter what gets retrieved per user. A single fine-tuned model can't selectively forget things for one customer while remembering them for another.
- You're still figuring out what you actually need. RAG lets you swap embedding models, adjust chunk sizes, try a new reranker, and see the effect same-day. No GPU training run required to iterate.

**Reach for fine-tuning when:**

- You need consistent *behavior*, not facts. A strict output schema, a specific tone, a house style that has to hold every single time. RAG doesn't touch how a model responds — it just changes what it has to work with.
- The thing you're teaching is a reasoning pattern, not a lookup. Clinical note structure, legal brief formatting, a proprietary coding convention — something the model needs to internalize as a skill rather than retrieve as a fact each time.
- You're running high volume at low latency and the task is narrow enough to compress into weights. A dedicated classifier or extractor doing one job at scale doesn't want the overhead of a retrieval hop on every call.

In practice, most systems I'd actually want to ship use both — lightweight fine-tuning (or just good instructions) for format and tone, RAG for facts that need to stay current and verifiable. Treating it as either/or is usually a false choice.

---

## 3. Where RAG actually breaks, and what fixes it

**Chunking gone wrong.** Sentences or table rows cut in half, so a fact that needed its neighbor for context gets orphaned in retrieval. Chunks too big and the embedding gets diluted — a 2000-token chunk about six different subtopics doesn't embed as any one of them well. Fix: structure-aware splitting (paragraph → sentence, not blind character counts), keep tables and code blocks atomic, add overlap, and just... test different chunk sizes against your actual corpus instead of assuming a number from a blog post applies to yours.

**Retrieval pulling the wrong thing, or missing the right thing.** Usually a vocabulary mismatch — the user asks "how do I cancel" and the doc says "termination procedure," and a weak embedding model doesn't bridge that gap. Or the model's fine on semantics but misses an exact SKU or error code because dense search just isn't built for exact matching. Fix: hybrid retrieval (what I did here), add a reranker over a wider candidate pool if precision's still off, consider query rewriting for genuinely mismatched phrasing, and don't be shy about testing a different embedding model — the default isn't always the right one for jargon-heavy domains.

**Context overflow.** Cramming ten chunks into the prompt because "more context can't hurt" — except it can. Long contexts have a well-documented "lost in the middle" problem where models pay less attention to stuff buried mid-prompt, and you're also just burning budget that could've gone to a higher-precision top-3. Fix: fewer, better-ranked chunks beats more mediocre ones. If a reranker still isn't tight enough, compress or summarize chunks before they hit the prompt rather than pasting them in raw.

**Hallucination even with good retrieval.** This one's sneaky because it looks like a retrieval failure when it's actually a generation failure — the right context was there and the model just didn't use it, filling gaps from its own memory instead. Fix: explicit "say you don't know" instructions (covered above, worth repeating because it matters that much), require citations for every claim since that forces the model to actually point at something, lower the temperature, and if you want a real safety net, run a faithfulness check afterward — an NLI model or a second LLM call checking whether each claim in the answer is actually entailed by what was retrieved.

---

## 4. Naive → Advanced → Modular → GraphRAG

**Naive RAG** is exactly the pipeline in section 1: embed, search, stuff the top-k into the prompt, generate. That's what's actually implemented in this scaffold, roughly — plus the hybrid retrieval, which already nudges it past strictly "naive." It's the baseline everything else improves on, and it's genuinely fine for simple, well-scoped corpora. It falls over on multi-hop questions and anything needing query understanding.

**Advanced RAG** bolts optimization onto both ends without changing the core shape. Before retrieval: rewrite or expand the query, maybe route it to the right index if you have several. After retrieval: rerank with a cross-encoder, trim or summarize what got pulled back so it's not wasting prompt space. Same retrieve-then-generate skeleton, just less naive about how the input query and the retrieved output get handled.

**Modular RAG** stops treating the pipeline as fixed and linear. Retrieve, rerank, route, verify — these become swappable, reorderable, loopable pieces. This is where you get iterative retrieval (search, notice something's still missing, search again with what you learned), routing between multiple sources (structured DB vs. vector index vs. live web, chosen per query type), and agentic setups where the model itself decides when to retrieve as part of a broader loop rather than retrieval being a mandatory first step every time.

**GraphRAG** swaps — or adds alongside — the flat vector index with a knowledge graph: entities and relationships extracted from the corpus, often with hierarchical summaries layered on top. The case for it is specific: questions that need multi-hop reasoning across entities ("how does X relate to Y, and how does that connect to Z") tend to fall apart under pure similarity search, because the related facts might be worded completely differently and sit nowhere near each other in embedding space. It's also notably better at "give me the big picture across everything" questions that naive chunk retrieval just can't answer, since chunk retrieval only ever surfaces fragments, never a synthesis. Cost is real, though — building and maintaining the graph means a lot of LLM calls at ingestion time, and it gets more expensive to keep current as the corpus changes.

---

## 5. How you actually know if it's working

Four metrics, roughly split between "did retrieval do its job" and "did generation do its job":

**Faithfulness** — does the answer stick to what was actually retrieved, or does it wander off into things the model just knows/assumes? Checked by breaking the answer into individual claims and verifying each one is actually supported by the retrieved context (an NLI model or LLM judge works for this).

**Answer relevance** — separate question from faithfulness: does the answer even address what was asked? A response can be perfectly faithful to the retrieved context and still miss the actual question if retrieval pulled adjacent-but-not-quite-right material.

**Context precision** — of what got retrieved, how much of it was actually useful, and was the useful stuff ranked near the top? This is a retrieval-quality metric, not a generation one.

**Context recall** — of everything needed to fully answer the question, how much did retrieval actually surface? Usually checked against a reference answer — what fraction of the reference's claims are backed by what got retrieved.

The useful part is using these to triage *where* a system is broken, not just tracking a score:

- Recall low → retrieval didn't find the right stuff. Chunking or retrieval strategy problem.
- Precision low → retrieval found the right stuff plus a pile of noise. Reranking or top-k problem.
- Faithfulness low despite good recall/precision → the context was fine and the model hallucinated anyway. Prompting or verification problem.
- Relevance low despite everything else being fine → grounded and faithful, just answering slightly the wrong question. Usually a query-understanding or prompt-instruction problem.

I'd rather run these four against 15-20 real labeled questions than eyeball a handful of outputs and assume it's working — it's caught real regressions for me before that "looks fine" would've missed.

---

## 6. What's actually in this repo

```
enterprise_rag_engine/
├── docs/RAG_STUDY.md      # this file
├── src/
│   ├── ingestion.py       # pypdf / pdfplumber -> cleaned Document objects
│   ├── chunking.py        # recursive splitter + overlap -> Chunk objects
│   ├── embedding.py       # sentence-transformers wrapper (+ offline fallback, see note below)
│   ├── vector_store.py    # chromadb persistence + similarity query
│   ├── retrieval.py       # hybrid dense + BM25, fused with RRF
│   └── pipeline.py        # wires it all together, builds the final prompt
├── data/
│   ├── corpus/            # sample_policy doc used for the test run
│   ├── chunks/
│   └── vector_store/      # persisted chroma index
├── tests/test_pipeline.py # smoke tests, all passing
└── requirements.txt
```

Ran it end to end against a small sample refund-policy doc with the query *"what's the refund window for annual plans and what happens to my data after I cancel?"* — it correctly pulled the chunk with the 30-day annual window and the chunk with the 90-day data retention note, and built a proper cited prompt from both. Test output's below if you want to see it without rerunning.

One honest caveat: this sandbox has no route to huggingface.co, so `embedding.py` can't actually pull down `all-MiniLM-L6-v2` here. It falls back to a deterministic hashing embedder just so the plumbing could be verified end to end — that fallback is bag-of-words, not semantic, and is clearly marked "do not ship this" in the code. Point `get_embedder()` at a real environment with network access and it'll use the actual sentence-transformers model as intended; nothing else in the pipeline needs to change.

Packages installed and import-verified: `pypdf`, `pdfplumber`, `sentence-transformers`, `chromadb`, `rank-bm25` (plus their dependencies — `torch`, `transformers`, `numpy` pulled in automatically).
