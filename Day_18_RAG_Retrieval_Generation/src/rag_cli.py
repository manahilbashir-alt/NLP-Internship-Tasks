from src.retrieval import retrieve
from src.prompt import (
    build_augmented_prompt,
    format_sources
)
from src.generator import generate_answer


def run_rag():

    print("=" * 60)
    print("SIMPLE RAG QUESTION ANSWERING SYSTEM")
    print("=" * 60)

    print("\nType 'exit' to quit.")

    while True:

        question = input(
            "\nEnter your question: "
        ).strip()

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        if not question:
            print(
                "Please enter a question."
            )
            continue

        # --------------------------------
        # Retrieval
        # --------------------------------

        print(
            "\n[1/3] Retrieving relevant documents..."
        )

        results = retrieve(
            question
        )

        # --------------------------------
        # Build augmented prompt
        # --------------------------------

        print(
            "[2/3] Building augmented prompt..."
        )

        prompt = build_augmented_prompt(
            question,
            results
        )

        # --------------------------------
        # Generate answer
        # --------------------------------

        print(
            "[3/3] Generating grounded answer..."
        )

        answer = generate_answer(
            prompt
        )

        # --------------------------------
        # Display answer
        # --------------------------------

        print("\n")
        print("=" * 60)
        print("GROUNDED ANSWER")
        print("=" * 60)

        print(answer)

        # --------------------------------
        # Display sources
        # --------------------------------

        sources = format_sources(
            results
        )

        print("\nSOURCES")
        print("-" * 60)

        for source in sources:
            print(
                f"- {source}"
            )

        # --------------------------------
        # Display retrieval information
        # --------------------------------

        print("\nRETRIEVED CHUNKS")
        print("-" * 60)

        documents = results["documents"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]

        for i in range(
            len(documents)
        ):

            similarity = (
                1 / (1 + distances[i])
            )

            print(
                f"#{i + 1} | "
                f"Similarity: "
                f"{similarity:.4f} | "
                f"Source: "
                f"{metadatas[i]['source']} | "
                f"Chunk: "
                f"{metadatas[i]['chunk_id']}"
            )


if __name__ == "__main__":

    run_rag()