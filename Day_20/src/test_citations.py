from citation_rag import CitationRAG


def main():

    print("=" * 80)
    print("DAY 20 - SOURCE CITATION TEST")
    print("=" * 80)

    rag = CitationRAG()

    questions = [
        "What is ChromaDB?",
        "What are embeddings?",
        "What is similarity search?",
    ]

    for number, question in enumerate(
        questions,
        start=1
    ):

        print("\n")
        print("=" * 80)
        print(
            f"QUESTION {number}"
        )
        print("=" * 80)

        print(
            f"\nQuestion: {question}"
        )

        result = rag.chat(
            question
        )

        print("\nAnswer:")
        print(
            result["answer"]
        )

        print("\nCITATIONS:")

        for citation in result["sources"]:

            print(
                f"  - {citation}"
            )

    # ========================================================
    # REQUIREMENT VERIFICATION
    # ========================================================

    print("\n")
    print("=" * 80)
    print("REQUIREMENT VERIFICATION")
    print("=" * 80)

    result = rag.chat(
        "What is ChromaDB?"
    )

    if result["sources"]:

        print(
            "\n[PASS] Retrieved source metadata"
        )

    else:

        print(
            "\n[FAIL] No source metadata"
        )

    all_have_filename = all(
        ".txt" in source
        for source in result["sources"]
    )

    if all_have_filename:

        print(
            "[PASS] Document filename included"
        )

    else:

        print(
            "[FAIL] Document filename missing"
        )

    all_have_page = all(
        "Page" in source
        for source in result["sources"]
    )

    if all_have_page:

        print(
            "[PASS] Page number included"
        )

    else:

        print(
            "[FAIL] Page number missing"
        )

    print("\n")
    print(
        "Source citation test completed."
    )


if __name__ == "__main__":

    main()