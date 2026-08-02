"""
scraper.py

Scrapes text from multiple web pages and stores the collected corpus
in data/input_corpus.txt.
"""

import time
import requests
from bs4 import BeautifulSoup

SOURCES = {
    "NEWS": [
        "https://en.wikipedia.org/wiki/COVID-19_pandemic",
    ],
    "SCIENCE": [
        "https://en.wikipedia.org/wiki/Exoplanet",
    ],
    "DIALOGUE": [
        "https://stackoverflow.com/questions/231767/what-does-the-yield-keyword-do",
    ],
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 "
        "(compatible; NLP-Learning-Bot/1.0; educational use)"
    )
}


def fetch_page_text(url: str) -> str:
    """
    Fetch and extract readable text from a web page.

    Parameters
    ----------
    url : str
        URL of the webpage.

    Returns
    -------
    str
        Extracted text content.
    """

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=10
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()

    paragraphs = soup.find_all(
        ["p", "h1", "h2", "h3"]
    )

    text = "\n".join(
        paragraph.get_text(strip=True)
        for paragraph in paragraphs
        if paragraph.get_text(strip=True)
    )

    return text


def build_corpus(output_path: str = "data/input_corpus.txt") -> None:
    """
    Build a corpus by collecting text from all configured sources.

    Parameters
    ----------
    output_path : str
        Output file path.
    """

    with open(output_path, "w", encoding="utf-8") as file:

        for domain, urls in SOURCES.items():

            file.write(f"### DOMAIN: {domain} ###\n")

            for url in urls:

                try:
                    print(f"Fetching [{domain}] {url}")

                    page_text = fetch_page_text(url)

                    file.write(page_text + "\n")

                except Exception as error:
                    print(f"Failed to fetch {url}")
                    print(error)

                time.sleep(1)

            file.write("\n")

    print(f"\nCorpus successfully saved to {output_path}")


def main() -> None:
    """
    Execute the corpus collection pipeline.
    """

    build_corpus()


if __name__ == "__main__":
    main()