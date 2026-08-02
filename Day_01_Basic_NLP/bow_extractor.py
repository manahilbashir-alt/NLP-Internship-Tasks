"""
bow_extractor.py

Implements a Bag-of-Words (BoW) feature extractor from scratch
without using sklearn's CountVectorizer.
"""

import re
from collections import defaultdict


def simple_sentence_split(text: str) -> list[str]:
    """
    Split text into sentences.

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    list[str]
        List of sentences.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [sentence for sentence in sentences if sentence]


def simple_word_tokenize(sentence: str) -> list[str]:
    """
    Tokenize a sentence into lowercase words.

    Parameters
    ----------
    sentence : str
        Input sentence.

    Returns
    -------
    list[str]
        List of word tokens.
    """
    return re.findall(r"[a-zA-Z']+", sentence.lower())


def build_vocabulary(sentence_tokens: list[list[str]]) -> list[str]:
    """
    Build a sorted vocabulary from all tokenized sentences.

    Parameters
    ----------
    sentence_tokens : list[list[str]]
        Tokenized sentences.

    Returns
    -------
    list[str]
        Sorted vocabulary.
    """
    vocabulary = set()

    for tokens in sentence_tokens:
        vocabulary.update(tokens)

    return sorted(vocabulary)


def sentence_to_bow(tokens: list[str]) -> dict:
    """
    Convert a list of tokens into a Bag-of-Words dictionary.

    Parameters
    ----------
    tokens : list[str]
        List of tokens.

    Returns
    -------
    dict
        Word-frequency dictionary.
    """
    frequency = defaultdict(int)

    for token in tokens:
        frequency[token] += 1

    return dict(frequency)


def build_bow_matrix(text: str):
    """
    Build the complete Bag-of-Words representation.

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    tuple
        Sentences, vocabulary, BoW dictionaries,
        and dense BoW matrix.
    """
    sentences = simple_sentence_split(text)

    sentence_tokens = [
        simple_word_tokenize(sentence)
        for sentence in sentences
    ]

    vocabulary = build_vocabulary(sentence_tokens)

    bow_dictionaries = [
        sentence_to_bow(tokens)
        for tokens in sentence_tokens
    ]

    matrix = []

    for bow in bow_dictionaries:
        row = [
            bow.get(word, 0)
            for word in vocabulary
        ]
        matrix.append(row)

    return (
        sentences,
        vocabulary,
        bow_dictionaries,
        matrix
    )


def main() -> None:
    """
    Generate and save the Bag-of-Words representation.
    """

    with open(
        "outputs/cleaned_corpus.txt",
        "r",
        encoding="utf-8"
    ) as file:
        _ = file.read()

    sample_text = (
        "Global markets surged as investors grew confident. "
        "Astronomers identified a rocky exoplanet in the habitable zone. "
        "Jordan fixed the tokenization bug but the lemmatizer still misbehaves. "
        "The lemmatizer bug confused irregular nouns."
    )

    (
        sentences,
        vocabulary,
        bow_dictionaries,
        matrix
    ) = build_bow_matrix(sample_text)

    lines = [
        "=" * 90,
        "BAG-OF-WORDS (FROM SCRATCH)",
        "=" * 90,
        f"\nVocabulary ({len(vocabulary)} words):\n{vocabulary}\n"
    ]

    for index, (sentence, bow) in enumerate(
        zip(sentences, bow_dictionaries),
        start=1
    ):
        lines.append(f"Sentence {index}: {sentence}")
        lines.append(f"BoW: {bow}\n")

    lines.append(
        "Dense BoW Matrix (rows = sentences, columns = vocabulary)"
    )

    for index, row in enumerate(matrix, start=1):
        lines.append(f"Sentence {index}: {row}")

    output = "\n".join(lines)

    print(output)

    with open(
        "outputs/bow_results.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(output)

    print("\nResults saved to outputs/bow_results.txt")


if __name__ == "__main__":
    main()