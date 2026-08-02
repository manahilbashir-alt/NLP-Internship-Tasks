"""
tfidf_from_scratch.py
---------------------
Day 2 Task 1

TF
IDF
TF-IDF

Implemented completely from scratch.
Only sklearn is used at the end for verification.
"""

import re
import math
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer


# -------------------------------------------------------
# Sentence Splitter
# -------------------------------------------------------

def simple_sentence_split(text):
    """Split text into sentences."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s for s in sentences if s]


# -------------------------------------------------------
# Tokenizer
# -------------------------------------------------------

def simple_word_tokenize(sentence):
    """Lowercase + keep alphabetic words."""
    return re.findall(r"[a-zA-Z']+", sentence.lower())


# -------------------------------------------------------
# Vocabulary
# -------------------------------------------------------

def build_vocabulary(sentences_tokens):
    vocab = set()

    for tokens in sentences_tokens:
        vocab.update(tokens)

    return sorted(vocab)


# -------------------------------------------------------
# Bag of Words
# -------------------------------------------------------

def sentence_to_bow(tokens):

    freq = defaultdict(int)

    for token in tokens:
        freq[token] += 1

    return dict(freq)


# -------------------------------------------------------
# Build BoW Matrix
# -------------------------------------------------------

def build_bow_matrix(text):

    sentences = simple_sentence_split(text)

    sentences_tokens = [
        simple_word_tokenize(sentence)
        for sentence in sentences
    ]

    vocab = build_vocabulary(sentences_tokens)

    bow_dicts = [
        sentence_to_bow(tokens)
        for tokens in sentences_tokens
    ]

    matrix = []

    for bow in bow_dicts:

        row = []

        for word in vocab:

            row.append(
                bow.get(word, 0)
            )

        matrix.append(row)

    return (
        sentences,
        sentences_tokens,
        vocab,
        bow_dicts,
        matrix
    )
# -------------------------------------------------------
# Term Frequency (TF)
# -------------------------------------------------------

def compute_tf(sentences_tokens):
    """
    Compute Term Frequency for every sentence.

    TF = (Count of word in document) /
         (Total words in document)
    """

    tf_list = []

    for tokens in sentences_tokens:

        bow = sentence_to_bow(tokens)

        total_words = len(tokens)

        tf = {}

        for word, count in bow.items():

            tf[word] = count / total_words

        tf_list.append(tf)

    return tf_list


# -------------------------------------------------------
# Document Frequency (DF)
# -------------------------------------------------------

def compute_document_frequency(sentences_tokens):
    """
    Count in how many documents
    each word appears.
    """

    df = defaultdict(int)

    for tokens in sentences_tokens:

        unique_words = set(tokens)

        for word in unique_words:

            df[word] += 1

    return dict(df)


# -------------------------------------------------------
# Inverse Document Frequency (IDF)
# -------------------------------------------------------

def compute_idf(sentences_tokens):
    """
    IDF = log(N / DF)

    N = total documents
    DF = documents containing the word
    """

    N = len(sentences_tokens)

    df = compute_document_frequency(sentences_tokens)

    idf = {}

    for word, freq in df.items():

        idf[word] = math.log(N / freq)

    return idf


# -------------------------------------------------------
# TF-IDF
# -------------------------------------------------------

def compute_tfidf(tf_list, idf):
    """
    TF-IDF = TF × IDF
    """

    tfidf_list = []

    for tf in tf_list:

        tfidf = {}

        for word, value in tf.items():

            tfidf[word] = value * idf[word]

        tfidf_list.append(tfidf)

    return tfidf_list
# -------------------------------------------------------
# MAIN PROGRAM
# -------------------------------------------------------

if __name__ == "__main__":

    # Read cleaned corpus
    with open("outputs/cleaned_corpus.txt", "r", encoding="utf-8") as f:
        text = f.read()

    # Build BoW
    (
        sentences,
        sentences_tokens,
        vocab,
        bow_dicts,
        matrix
    ) = build_bow_matrix(text)

    # Compute TF
    tf_list = compute_tf(sentences_tokens)

    # Compute IDF
    idf = compute_idf(sentences_tokens)

    # Compute TF-IDF
    tfidf_list = compute_tfidf(tf_list, idf)

    # ---------------------------------------------------
    # PRINT RESULTS
    # ---------------------------------------------------

    lines = []
    lines.append("=" * 90)
    lines.append("TF-IDF FROM SCRATCH")
    lines.append("=" * 90)

    lines.append(f"\nTotal Documents: {len(sentences)}")
    lines.append(f"Vocabulary Size : {len(vocab)}\n")

    for i in range(min(5, len(sentences))):

        lines.append("-" * 90)
        lines.append(f"Document {i+1}")
        lines.append("-" * 90)

        lines.append(f"\nSentence:\n{sentences[i]}\n")

        lines.append("Bag of Words:")
        lines.append(str(bow_dicts[i]))

        lines.append("\nTF:")
        lines.append(str(tf_list[i]))

        lines.append("\nTF-IDF:")
        lines.append(str(tfidf_list[i]))

        lines.append("\n")

    # ---------------------------------------------------
    # PRINT IDF
    # ---------------------------------------------------

    lines.append("=" * 90)
    lines.append("IDF VALUES")
    lines.append("=" * 90)

    for word in sorted(idf):

        lines.append(
            f"{word:<20} {idf[word]:.4f}"
        )

    # ---------------------------------------------------
    # VERIFY USING SKLEARN
    # ---------------------------------------------------

    lines.append("\n")
    lines.append("=" * 90)
    lines.append("SKLEARN VERIFICATION")
    lines.append("=" * 90)

    vectorizer = TfidfVectorizer()

    sklearn_matrix = vectorizer.fit_transform(sentences)

    feature_names = vectorizer.get_feature_names_out()

    lines.append(
        f"Shape : {sklearn_matrix.shape}"
    )

    lines.append(
        f"Vocabulary Size : {len(feature_names)}"
    )

    lines.append(
        "\nFirst 20 vocabulary words:"
    )

    lines.append(
        str(feature_names[:20])
    )

    output = "\n".join(lines)

    print(output)

    with open(
        "outputs/tfidf_results.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(output)

    print("\nResults saved to outputs/tfidf_results.txt")        