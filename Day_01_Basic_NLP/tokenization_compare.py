"""
tokenization_compare.py

Compares character-level, word-level, BPE, and WordPiece tokenization.
"""

from nltk.tokenize import word_tokenize
from tokenizers import Tokenizer, models, pre_tokenizers, trainers

SAMPLE_SENTENCES = [
    "Researchers discovered an unbelievably habitable exoplanet.",
    "The tokenization bug is retokenizing incorrectly.",
    "Jordan's lemmatizer misclassifies irregular nouns like mice.",
]


def char_level_tokenize(text: str) -> list[str]:
    """
    Split text into individual characters.

    Parameters
    ----------
    text : str
        Input sentence.

    Returns
    -------
    list[str]
        Character-level tokens.
    """
    return list(text)


def word_level_tokenize(text: str) -> list[str]:
    """
    Split text into word tokens using NLTK.

    Parameters
    ----------
    text : str
        Input sentence.

    Returns
    -------
    list[str]
        Word-level tokens.
    """
    return word_tokenize(text)


def train_bpe_tokenizer(
    corpus_path: str,
    vocab_size: int = 300
) -> Tokenizer:
    """
    Train a Byte Pair Encoding (BPE) tokenizer.

    Parameters
    ----------
    corpus_path : str
        Path to the training corpus.

    vocab_size : int
        Vocabulary size.

    Returns
    -------
    Tokenizer
        Trained BPE tokenizer.
    """

    tokenizer = Tokenizer(
        models.BPE(unk_token="[UNK]")
    )

    tokenizer.pre_tokenizer = (
        pre_tokenizers.Whitespace()
    )

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        special_tokens=[
            "[UNK]",
            "[PAD]"
        ]
    )

    tokenizer.train(
        [corpus_path],
        trainer
    )

    return tokenizer


def train_wordpiece_tokenizer(
    corpus_path: str,
    vocab_size: int = 300
) -> Tokenizer:
    """
    Train a WordPiece tokenizer.

    Parameters
    ----------
    corpus_path : str
        Path to the training corpus.

    vocab_size : int
        Vocabulary size.

    Returns
    -------
    Tokenizer
        Trained WordPiece tokenizer.
    """

    tokenizer = Tokenizer(
        models.WordPiece(
            unk_token="[UNK]"
        )
    )

    tokenizer.pre_tokenizer = (
        pre_tokenizers.Whitespace()
    )

    trainer = trainers.WordPieceTrainer(
        vocab_size=vocab_size,
        special_tokens=[
            "[UNK]",
            "[PAD]",
            "[CLS]",
            "[SEP]"
        ]
    )

    tokenizer.train(
        [corpus_path],
        trainer
    )

    return tokenizer


def main() -> None:
    """
    Compare different tokenization techniques.
    """

    corpus_path = "outputs/cleaned_corpus.txt"

    bpe_tokenizer = train_bpe_tokenizer(corpus_path)

    wordpiece_tokenizer = train_wordpiece_tokenizer(
        corpus_path
    )

    lines = [
        "=" * 90,
        "TOKENIZATION COMPARISON",
        "=" * 90
    ]

    for sentence in SAMPLE_SENTENCES:

        lines.append(f"\nSentence: {sentence}")

        character_tokens = char_level_tokenize(sentence)

        word_tokens = word_level_tokenize(sentence)

        bpe_tokens = (
            bpe_tokenizer
            .encode(sentence)
            .tokens
        )

        wordpiece_tokens = (
            wordpiece_tokenizer
            .encode(sentence)
            .tokens
        )

        lines.append(
            f"Character Tokens ({len(character_tokens)}): {character_tokens}"
        )

        lines.append(
            f"Word Tokens ({len(word_tokens)}): {word_tokens}"
        )

        lines.append(
            f"BPE Tokens ({len(bpe_tokens)}): {bpe_tokens}"
        )

        lines.append(
            f"WordPiece Tokens ({len(wordpiece_tokens)}): {wordpiece_tokens}"
        )

    output = "\n".join(lines)

    print(output)

    with open(
        "outputs/tokenization_comparison.txt",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(output)

    print("\nResults saved to outputs/tokenization_comparison.txt")


if __name__ == "__main__":
    main()