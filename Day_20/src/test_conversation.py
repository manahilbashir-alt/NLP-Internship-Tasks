from conversation_rag import ConversationalRAG


def main():

    print("=" * 80)
    print("DAY 20 - CONVERSATIONAL RAG TEST")
    print("=" * 80)

    rag = ConversationalRAG()

    session_id = "demo_session"

    print("\n" + "=" * 80)
    print("TURN 1")
    print("=" * 80)

    question_1 = "What is ChromaDB?"

    result_1 = rag.chat(
        session_id,
        question_1
    )

    print(
        f"\nQuestion: {result_1['question']}"
    )

    print(
        f"Contextualized question: "
        f"{result_1['contextualized_question']}"
    )

    print(
        f"\nAnswer:\n{result_1['answer']}"
    )

    print(
        f"\nHistory messages: "
        f"{result_1['history_length']}"
    )

    print("\n" + "=" * 80)
    print("TURN 2 - FOLLOW-UP QUESTION")
    print("=" * 80)

    question_2 = "What about the second point?"

    result_2 = rag.chat(
        session_id,
        question_2
    )

    print(
        f"\nQuestion: {result_2['question']}"
    )

    print(
        f"Contextualized question: "
        f"{result_2['contextualized_question']}"
    )

    print(
        f"\nAnswer:\n{result_2['answer']}"
    )

    print(
        f"\nHistory messages: "
        f"{result_2['history_length']}"
    )

    print("\n" + "=" * 80)
    print("CONVERSATIONAL RAG TEST COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()