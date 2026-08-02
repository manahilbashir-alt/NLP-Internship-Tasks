# NLP Text Preprocessing Pipeline – Day 1 Internship

## Project Overview

This project was completed as part of my Day 1 internship tasks. The objective was to build and execute a basic Natural Language Processing (NLP) preprocessing pipeline using Python. The pipeline demonstrates essential preprocessing techniques commonly used before training NLP and Machine Learning models.

The project includes text cleaning, tokenization comparison, stemming and lemmatization, Part-of-Speech (POS) tagging, and Bag-of-Words (BoW) feature extraction.

---

## Objectives

- Create an NLP preprocessing pipeline.
- Clean and normalize raw text data.
- Compare different tokenization techniques.
- Understand the difference between stemming and lemmatization.
- Perform Part-of-Speech (POS) tagging.
- Generate Bag-of-Words (BoW) representations.
- Analyze the strengths and limitations of different tokenization methods.

---

## Technologies Used

- Python 3
- NLTK
- spaCy
- en_core_web_sm
- Regular Expressions (re)

---

## Project Structure

```text
internship-day1-nlp-pipeline
│
├── README.md
├── Assignment.md
├── Day1_Report.pdf
│
├── clean_text.py
├── tokenization_compare.py
├── stem_lemma_compare.py
├── pos_tagging.py
├── bow_extractor.py
├── scraper.py
│
├── data
│   └── input_corpus.txt
│
├── outputs
│   ├── cleaned_corpus.txt
│   ├── tokenization_comparison.txt
│   ├── stem_lemma_comparison.txt
│   ├── stem_lemma_corpus_sample.txt
│   ├── pos_tagging_results.txt
│   └── bow_results.txt
```

---

## Tasks Performed

### 1. Text Cleaning

The raw corpus was cleaned by removing unnecessary characters and normalizing the text before further processing.

**Output**

```
outputs/cleaned_corpus.txt
```

---

### 2. Tokenization Comparison

Four tokenization methods were compared:

- Character-level
- Word-level
- Byte Pair Encoding (BPE)
- WordPiece

The comparison demonstrates how each tokenizer processes the same sentence differently.

**Output**

```
outputs/tokenization_comparison.txt
```

---

### 3. Stemming and Lemmatization

Words were processed using both stemming and lemmatization to compare their outputs.

Examples include:

- running → run
- studies → study
- wolves → wolf
- mice → mouse

**Output**

```
outputs/stem_lemma_comparison.txt
outputs/stem_lemma_corpus_sample.txt
```

---

### 4. Part-of-Speech Tagging

spaCy was used to identify grammatical categories such as:

- Nouns
- Verbs
- Adjectives
- Adverbs

**Output**

```
outputs/pos_tagging_results.txt
```

---

### 5. Bag-of-Words (BoW)

A simple Bag-of-Words representation was generated from sample sentences.

The output includes:

- Vocabulary
- Word frequency dictionary
- Dense BoW matrix

**Output**

```
outputs/bow_results.txt
```

---

## Results

The NLP preprocessing pipeline executed successfully.

The generated outputs demonstrate:

- Cleaned text corpus
- Comparison of multiple tokenization techniques
- Differences between stemming and lemmatization
- POS tagging results
- Bag-of-Words representation

---

## Observations

- Character-level tokenization generated the highest number of tokens.
- Word-level tokenization preserved complete words but may struggle with unseen vocabulary.
- BPE and WordPiece produced meaningful subword units, making them more suitable for modern NLP models.
- Stemming reduced words to their root forms, while lemmatization produced valid dictionary words whenever possible.

---

## Challenges Encountered

During the setup process, a few dependencies were missing.

The following issues were resolved before executing the pipeline successfully:

- Installed the NLTK package.
- Downloaded the required NLTK resources (`punkt_tab` and `stopwords`).
- Installed spaCy.
- Downloaded the `en_core_web_sm` language model.

No issues were found in the generated outputs after completing the setup.

---

## How to Run

Clone the repository:

```bash
git clone https://github.com/manahilbashir-alt/internship-day1-nlp-pipeline.git
```

Move into the project directory:

```bash
cd internship-day1-nlp-pipeline
```

Run each script individually:

```bash
python clean_text.py

python tokenization_compare.py

python stem_lemma_compare.py

python pos_tagging.py

python bow_extractor.py
```

---

## Learning Outcomes

Through this project, I learned:

- Basic NLP preprocessing techniques.
- Practical use of NLTK and spaCy.
- Differences between character, word, and subword tokenization.
- The distinction between stemming and lemmatization.
- Feature extraction using the Bag-of-Words model.
- Managing Python dependencies required for NLP workflows.

---

## Author

**Manahil Bashir**

BS Computer Science

FAST – National University of Computer and Emerging Sciences

NLP Internship – Day 1