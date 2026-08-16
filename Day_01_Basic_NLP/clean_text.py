"""
clean_text.py
-------------

This module cleans raw text collected from web pages by removing
HTML tags, Markdown formatting, numbers, unnecessary special
characters, and extra whitespace.

The cleaned text is saved to:
    outputs/cleaned_corpus.txt
"""

import re


def strip_html(text: str) -> str:
    """
    Remove HTML tags from the input text.

    Parameters
    ----------
    text : str
        Raw text containing HTML tags.

    Returns
    -------
    str
        Text with HTML tags removed.
    """
    return re.sub(r"<[^>]+>", " ", text)


def strip_markdown(text: str) -> str:
    """
    Remove common Markdown formatting.

    Removes:
    - Headers (#, ##, ### ...)
    - Bold (**text**)
    - Italic (*text*)
    - Underscore formatting (_text_)

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    str
        Text without Markdown formatting.
    """
    text = re.sub(r"#{1,6}\s*", "", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"\*(.*?)\*", r"\1", text)
    text = re.sub(r"_(.*?)_", r"\1", text)

    return text


def strip_numbers(text: str) -> str:
    """
    Remove all numeric digits from the text.

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    str
        Text with numbers removed.
    """
    return re.sub(r"\d+", "", text)


def strip_special_characters(text: str) -> str:
    """
    Remove unwanted special characters while preserving
    letters, digits, whitespace, and basic sentence punctuation.

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    str
        Cleaned text.
    """
    return re.sub(r"[^a-zA-Z0-9\s.,!?']", " ", text)


def normalize_whitespace(text: str) -> str:
    """
    Replace multiple spaces or newlines with a single space.

    Parameters
    ----------
    text : str
        Input text.

    Returns
    -------
    str
        Text with normalized whitespace.
    """
    return re.sub(r"\s+", " ", text).strip()


def clean_pipeline(text: str) -> str:
    """
    Execute the complete text cleaning pipeline.

    Cleaning steps:
    1. Remove HTML tags
    2. Remove Markdown formatting
    3. Remove numbers
    4. Remove unwanted special characters
    5. Normalize whitespace

    Parameters
    ----------
    text : str
        Raw input text.

    Returns
    -------
    str
        Fully cleaned text.
    """

    text = strip_html(text)
    text = strip_markdown(text)
    text = strip_numbers(text)
    text = strip_special_characters(text)
    text = normalize_whitespace(text)

    return text


def main() -> None:
    """
    Read the raw corpus, clean it, save the cleaned
    version, and display a preview.
    """

    with open("data/input_corpus.txt", "r", encoding="utf-8") as file:
        raw_text = file.read()

    cleaned_text = clean_pipeline(raw_text)

    with open("outputs/cleaned_corpus.txt", "w", encoding="utf-8") as file:
        file.write(cleaned_text)

    print("=" * 70)
    print("RAW TEXT (First 300 Characters)")
    print("=" * 70)
    print(raw_text[:300])

    print("\n" + "=" * 70)
    print("CLEANED TEXT (First 300 Characters)")
    print("=" * 70)
    print(cleaned_text[:300])

    print("\nCleaned corpus saved to:")
    print("outputs/cleaned_corpus.txt")


if __name__ == "__main__":
    main()