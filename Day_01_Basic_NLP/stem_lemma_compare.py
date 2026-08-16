"""
stem_lemma_compare.py

Compares stemming and lemmatization after removing stopwords.
"""

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import word_tokenize

STEMMER = PorterStemmer()
LEMMATIZER = WordNetLemmatizer()
STOP_WORDS = set(stopwords.words("english"))


def remove_stopwords(tokens: list[str]) -> list[str]:
    """
    Remove English stopwords from a list of tokens.

    Parameters
    ----------
    tokens : list[str]
        Input tokens.

    Returns
    -------
    list[str]
        Tokens after stopword removal.
    """
    return [
        token
        for token in tokens
        if token.lower() not in STOP_WORDS
    ]


def compare_stem_lemma(tokens: list[str]) -> list[tuple]:
    """
    Compare stemming and lemmatization.

    Parameters
    ----------
    tokens : list[str]
        List of words.

    Returns
    -------
    list[tuple]
        Original word, stemmed word, and lemmatized word.
    """

    results = []

    for token in tokens:

        stemmed_word = STEMMER.stem(token)

        lemmatized_word = LEMMATIZER.lemmatize(
            token.lower()
        )

        results.append(
            (
                token,
                stemmed_word,
                lemmatized_word
            )
        )

    return results


def main() -> None:
    """
    Demonstrate stemming and lemmatization.
    """

    with open(
        "outputs/cleaned_corpus.txt",
        "r",
        encoding="utf-8"
    ) as file:

        text = file.read()

    tokens = word_tokenize(text)

    filtered_tokens = remove_stopwords(tokens)

    print(f"Original Tokens : {len(tokens)}")
    print(f"Without Stopwords : {len(filtered_tokens)}")

    sample_words = [
        "running",
        "runs",
        "ran",
        "studies",
        "studying",
        "better",
        "discoveries",
        "orbiting",
        "researchers",
        "mice",
        "cutting",
        "wolves",
        "flies",
        "happier",
        "children",
        "confirmed",
    ]

    comparison = compare_stem_lemma(sample_words)

    print()

    print(f"{'Word':<15}{'Stemmed':<15}{'Lemmatized':<15}")

    print("-" * 45)

    report_lines = [
        f"{'Word':<15}{'Stemmed':<15}{'Lemmatized':<15}",
        "-" * 45,
    ]

    for word, stem, lemma in comparison:

        line = f"{word:<15}{stem:<15}{lemma:<15}"

        print(line)

        report_lines.append(line)

    with open(
        "outputs/stem_lemma_comparison.txt",
        "w",
        encoding="utf-8"
    ) as file:

        file.write("\n".join(report_lines))

    corpus_sample = compare_stem_lemma(
        filtered_tokens[:40]
    )

    with open(
        "outputs/stem_lemma_corpus_sample.txt",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            f"{'Word':<15}{'Stemmed':<15}{'Lemmatized':<15}\n"
        )

        file.write("-" * 45 + "\n")

        for word, stem, lemma in corpus_sample:

            file.write(
                f"{word:<15}{stem:<15}{lemma:<15}\n"
            )

    print(
        "\nResults saved to "
        "outputs/stem_lemma_comparison.txt "
        "and outputs/stem_lemma_corpus_sample.txt"
    )


if __name__ == "__main__":
    main()