"""
pos_tagging.py

Performs Part-of-Speech (POS) tagging using spaCy and groups
tokens into grammatical categories.
"""

import spacy

NLP_MODEL = spacy.load("en_core_web_sm")

SAMPLE_SENTENCES = [
    "Global markets surged as investors grew more confident about rate cuts.",
    "Astronomers identified a rocky exoplanet orbiting within the habitable zone.",
    "Jordan fixed the tokenization bug but the lemmatizer still misbehaves.",
]


def tag_sentence(sentence: str) -> list[tuple]:
    """
    Perform Part-of-Speech tagging on a sentence.

    Parameters
    ----------
    sentence : str
        Input sentence.

    Returns
    -------
    list[tuple]
        Each tuple contains:
        (token, coarse POS, detailed POS tag, explanation)
    """

    document = NLP_MODEL(sentence)

    return [
        (
            token.text,
            token.pos_,
            token.tag_,
            spacy.explain(token.pos_)
        )
        for token in document
    ]


def bucket_by_category(sentence: str) -> dict:
    """
    Group tokens into grammatical categories.

    Parameters
    ----------
    sentence : str
        Input sentence.

    Returns
    -------
    dict
        Dictionary containing grouped tokens.
    """

    document = NLP_MODEL(sentence)

    buckets = {
        "NOUN": [],
        "VERB": [],
        "ADJ": [],
        "ADV": [],
        "OTHER": [],
    }

    for token in document:

        if token.pos_ in buckets:

            buckets[token.pos_].append(token.text)

        elif token.pos_ == "PROPN":

            buckets["NOUN"].append(token.text)

        else:

            buckets["OTHER"].append(
                (
                    token.text,
                    token.pos_
                )
            )

    return buckets


def main() -> None:
    """
    Run POS tagging on sample sentences and save the results.
    """

    lines = [
        "=" * 90,
        "PART-OF-SPEECH TAGGING RESULTS",
        "=" * 90,
    ]

    for sentence in SAMPLE_SENTENCES:

        lines.append(f"\nSentence: {sentence}")

        lines.append(
            f"{'Token':<15}{'POS':<8}{'Tag':<8}Explanation"
        )

        lines.append("-" * 70)

        tagged_tokens = tag_sentence(sentence)

        for token, pos, tag, explanation in tagged_tokens:

            lines.append(
                f"{token:<15}{pos:<8}{tag:<8}{explanation}"
            )

        buckets = bucket_by_category(sentence)

        lines.append(f"\nNouns      : {buckets['NOUN']}")
        lines.append(f"Verbs      : {buckets['VERB']}")
        lines.append(f"Adjectives : {buckets['ADJ']}")
        lines.append(f"Adverbs    : {buckets['ADV']}")
        lines.append(f"Other      : {buckets['OTHER']}")

    output = "\n".join(lines)

    print(output)

    with open(
        "outputs/pos_tagging_results.txt",
        "w",
        encoding="utf-8"
    ) as file:

        file.write(output)

    print("\nResults saved to outputs/pos_tagging_results.txt")


if __name__ == "__main__":
    main()