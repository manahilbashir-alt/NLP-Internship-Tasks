# Day 03: N-gram, LSTM and Transformer Experiments

## Overview

This project contains experiments on different Natural Language Processing
approaches, starting from traditional statistical language models and moving
towards modern transformer-based representations.

The tasks demonstrate:
- Language modeling using N-grams
- Contextual embeddings using BERT
- Gradient flow analysis in LSTM
- Similarity comparison between different text representations
- Visualization of static vs contextual embeddings using t-SNE


---

# Task 1: N-gram Language Model (Bigram & Trigram)

## Objective

Build a simple language model using:
- Bigram probabilities
- Trigram probabilities

The purpose is to understand how traditional NLP models predict the next word
using previous word context.

## Method

Steps performed:

1. Loaded text corpus
2. Tokenized sentences
3. Built vocabulary
4. Created bigram and trigram counts
5. Calculated probabilities
6. Generated predictions


## Observation

Bigram models only consider one previous word, while trigram models consider
two previous words and capture more context.


---

# Task 2: Transformer Embeddings (BERT)

## Objective

Generate contextual word representations using a pretrained transformer model.

## Method

The experiment used sentences containing the word "bank":

Example:

"I deposited money in the bank."

"I sat near the bank of the river."


BERT embeddings were generated for both sentences.

## Observation

Traditional embeddings assign one fixed vector to a word, while transformers
generate different representations depending on surrounding context.

The word "bank" receives different embeddings for financial and river meanings.


## Output

Attached:
- Tokenization results
- Embedding size
- Context comparison


---

# Task 3: LSTM Gradient Flow Analysis

## Objective

Study how gradients move through an LSTM network and observe the vanishing
gradient problem.

## Method

A simple LSTM model was created:

- Input size: 10
- Hidden size: 20
- Sequence length: 60


The model performed:

1. Forward pass
2. Loss calculation
3. Backward propagation
4. Gradient magnitude calculation for each token


## Observation

Early tokens had very small gradients while later tokens had larger gradients.

Example:

Token 1:
very small gradient

Token 60:
larger gradient


This shows the vanishing gradient problem in sequential models.


## Output

Attached:
- Gradient magnitude graph


---

# Task 4: Similarity Comparison

## Objective

Compare different NLP representations using cosine similarity.

Methods compared:

1. TF-IDF
2. Static embedding (Word2Vec style)
3. N-gram representation
4. Transformer embedding


## Test Cases

### Synonym Test

Sentence 1:

"The movie was very good."

Sentence 2:

"The film was very excellent."


### Polysemy Test

Sentence 1:

"I deposited money in the bank."

Sentence 2:

"I sat near the bank of the river."


## Observation

Transformer embeddings achieved higher similarity for synonyms because they
understand semantic meaning.

For polysemy, transformer embeddings performed better because they consider
context.


## Output

Attached:
- Final cosine similarity comparison table


---

# Task 5: t-SNE Visualization

## Objective

Visualize the difference between static and contextual embeddings.

## Method

The ambiguous word "bank" was used in different contexts.

Finance examples:

- I deposited money in the bank.
- The bank approved my loan.


River examples:

- I sat near the bank of the river.
- The boat reached the river bank.


Embeddings were generated using:

1. Static representation
2. Transformer representation


Then t-SNE was applied to reduce embeddings into 2D space.


## Observation

Static embeddings keep different meanings closer because the word has one
fixed representation.

Transformer embeddings separate meanings because the representation changes
according to context.

---

# Conclusion

These experiments show the evolution of NLP techniques:

N-gram
    ↓
TF-IDF
    ↓
Static Embeddings
    ↓
LSTM
    ↓
Transformer Models


Traditional methods depend on word frequency and fixed representations,
while transformer models capture meaning using context.