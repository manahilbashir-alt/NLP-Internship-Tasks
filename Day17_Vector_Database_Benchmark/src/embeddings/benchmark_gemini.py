import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CHUNK_DIR = BASE_DIR / "data" / "chunks"
OUTPUT_DIR = BASE_DIR / "output" / "benchmarks"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "gemini-embedding-001"

BATCH_SIZE = 20


# ============================================================
# 20 QUESTIONS
# ============================================================

QUESTIONS = [
    {
        "question": "Who is Mr. Bingley?",
        "keywords": ["Bingley", "young man", "fortune"]
    },
    {
        "question": "Who is Elizabeth Bennet?",
        "keywords": ["Elizabeth", "Bennet"]
    },
    {
        "question": "Who is Jane Bennet?",
        "keywords": ["Jane", "Bennet"]
    },
    {
        "question": "Who is Mr. Bennet married to?",
        "keywords": ["Mrs. Bennet", "wife"]
    },
    {
        "question": "Where does Mr. Bingley move?",
        "keywords": ["Netherfield", "Park"]
    },
    {
        "question": "What is Netherfield Park?",
        "keywords": ["Netherfield", "house", "estate"]
    },
    {
        "question": "How wealthy is Mr. Bingley?",
        "keywords": ["four", "five", "thousand", "year"]
    },
    {
        "question": "Why is Mrs. Bennet excited about Mr. Bingley?",
        "keywords": ["daughters", "marry", "fortune"]
    },
    {
        "question": "Who tells Mrs. Bennet that Netherfield has been rented?",
        "keywords": ["Mrs. Long"]
    },
    {
        "question": "What is Mr. Bennet's reaction to hearing about Mr. Bingley?",
        "keywords": ["Mr. Bennet"]
    },
    {
        "question": "Is Mr. Bingley married?",
        "keywords": ["single"]
    },
    {
        "question": "Where did Mr. Bingley come from?",
        "keywords": ["north", "England"]
    },
    {
        "question": "Who is Mr. Darcy?",
        "keywords": ["Darcy"]
    },
    {
        "question": "What is Mr. Darcy's relationship with Mr. Bingley?",
        "keywords": ["Darcy", "Bingley"]
    },
    {
        "question": "What does Mrs. Bennet hope will happen to her daughters?",
        "keywords": ["marrying", "daughters"]
    },
    {
        "question": "Who is Mr. Collins?",
        "keywords": ["Mr. Collins"]
    },
    {
        "question": "What is Mr. Collins's relationship to the Bennet family?",
        "keywords": ["cousin", "Bennet"]
    },
    {
        "question": "What does Mr. Bennet think about his wife's excitement?",
        "keywords": ["Mr. Bennet", "wife"]
    },
    {
        "question": "What does Mr. Bingley take possession of?",
        "keywords": ["Netherfield", "possession"]
    },
    {
        "question": "Who are the Bennet daughters?",
        "keywords": ["Bennet", "daughters"]
    },
]


# ============================================================
# LOAD CHUNKS
# ============================================================

def load_chunks():

    chunks = []

    for file in sorted(
        CHUNK_DIR.glob("*.json")
    ):

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        if isinstance(data, list):
            chunks.extend(data)

        elif isinstance(data, dict):

            if "chunks" in data:
                chunks.extend(data["chunks"])

            else:
                chunks.append(data)

    return chunks


# ============================================================
# GEMINI EMBEDDING
# ============================================================

def embed_texts(client, texts):

    all_embeddings = []

    for start in range(
        0,
        len(texts),
        BATCH_SIZE
    ):

        batch = texts[
            start:start + BATCH_SIZE
        ]

        print(
            f"Embedding "
            f"{start + 1}-{min(start + BATCH_SIZE, len(texts))}"
            f"/{len(texts)}"
        )

        result = client.models.embed_content(
            model=MODEL_NAME,
            contents=batch,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=768
            )
        )

        for embedding in result.embeddings:

            all_embeddings.append(
                embedding.values
            )

    return np.asarray(
        all_embeddings,
        dtype="float32"
    )


def embed_query(client, text):

    result = client.models.embed_content(
        model=MODEL_NAME,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY",
            output_dimensionality=768
        )
    )

    return np.asarray(
        result.embeddings[0].values,
        dtype="float32"
    )


# ============================================================
# RELEVANCE
# ============================================================

def is_relevant(text, keywords):

    text_lower = text.lower()

    matches = sum(
        keyword.lower() in text_lower
        for keyword in keywords
    )

    required = max(
        1,
        len(keywords) // 2
    )

    return matches >= required


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 70)
    print("GEMINI EMBEDDING RETRIEVAL BENCHMARK")
    print("=" * 70)

    load_dotenv(
        BASE_DIR / ".env"
    )

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    if not api_key:

        raise RuntimeError(
            "GEMINI_API_KEY not found."
        )

    client = genai.Client(
        api_key=api_key
    )

    chunks = load_chunks()

    print(
        f"\nDocument chunks: "
        f"{len(chunks)}"
    )

    texts = [
        chunk.get("text", "")
        for chunk in chunks
    ]

    # --------------------------------------------------------
    # Document embeddings
    # --------------------------------------------------------

    print(
        "\nCreating Gemini document embeddings..."
    )

    start = time.perf_counter()

    document_embeddings = embed_texts(
        client,
        texts
    )

    embedding_time = (
        time.perf_counter() - start
    )

    print(
        f"\nEmbedding shape: "
        f"{document_embeddings.shape}"
    )

    print(
        f"Embedding time: "
        f"{embedding_time:.3f} seconds"
    )

    # Normalize
    document_embeddings /= np.linalg.norm(
        document_embeddings,
        axis=1,
        keepdims=True
    )

    # --------------------------------------------------------
    # 20 questions
    # --------------------------------------------------------

    results = []

    print(
        "\nRunning 20 retrieval questions..."
    )

    for number, question_data in enumerate(
        QUESTIONS,
        start=1
    ):

        question = question_data[
            "question"
        ]

        keywords = question_data[
            "keywords"
        ]

        print(
            f"\n[{number}/20] {question}"
        )

        start = time.perf_counter()

        query_embedding = embed_query(
            client,
            question
        )

        query_embedding /= np.linalg.norm(
            query_embedding
        )

        similarities = (
            document_embeddings
            @ query_embedding
        )

        top_indices = np.argsort(
            similarities
        )[-3:][::-1]

        query_time = (
            time.perf_counter() - start
        )

        relevant = 0

        for index in top_indices:

            if is_relevant(
                texts[index],
                keywords
            ):

                relevant += 1

        precision = relevant / 3

        results.append({

            "model": MODEL_NAME,

            "question": question,

            "relevant_top3": relevant,

            "top3_precision":
                round(
                    precision,
                    4
                ),

            "query_time_ms":
                round(
                    query_time * 1000,
                    4
                )
        })

    # --------------------------------------------------------
    # Save detailed results
    # --------------------------------------------------------

    df = pd.DataFrame(
        results
    )

    detailed_file = (
        OUTPUT_DIR
        / "gemini_retrieval_detailed.csv"
    )

    df.to_csv(
        detailed_file,
        index=False
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    average_precision = (
        df["top3_precision"].mean()
    )

    average_query_time = (
        df["query_time_ms"].mean()
    )

    summary = pd.DataFrame([
        {
            "model": MODEL_NAME,

            "embedding_dimension":
                document_embeddings.shape[1],

            "average_top3_precision":
                average_precision,

            "precision_percent":
                average_precision * 100,

            "average_query_time_ms":
                average_query_time,

            "embedding_time_seconds":
                embedding_time
        }
    ])

    summary_file = (
        OUTPUT_DIR
        / "gemini_retrieval_summary.csv"
    )

    summary.to_csv(
        summary_file,
        index=False
    )

    print("\n" + "=" * 70)
    print("GEMINI RESULTS")
    print("=" * 70)

    print(
        summary.to_string(
            index=False
        )
    )

    print(
        f"\nDetailed results:\n"
        f"{detailed_file}"
    )

    print(
        f"\nSummary:\n"
        f"{summary_file}"
    )


if __name__ == "__main__":
    main()