import json
import requests


API_URL = "http://127.0.0.1:8000/api/rag/chat"


# ============================================================
# 10 INDEPENDENT MULTI-TURN CONVERSATIONS
# ============================================================

conversations = [

    {
        "id": "conversation_1",
        "questions": [
            "Who is Mr. Bingley?",
            "What is his relationship with Jane Bennet?",
            "How does his friendship with Mr. Darcy affect this?"
        ]
    },

    {
        "id": "conversation_2",
        "questions": [
            "Who is Elizabeth Bennet?",
            "How does she initially feel about Mr. Darcy?",
            "What causes her opinion of him to change?"
        ]
    },

    {
        "id": "conversation_3",
        "questions": [
            "Who is Mr. Wickham?",
            "What does he claim about Mr. Darcy?",
            "How does Elizabeth react to his story?"
        ]
    },

    {
        "id": "conversation_4",
        "questions": [
            "Who is Jane Bennet?",
            "What does she think about Mr. Bingley's feelings?",
            "Why does Elizabeth have a different view?"
        ]
    },

    {
        "id": "conversation_5",
        "questions": [
            "What is Longbourn?",
            "Who lives there?",
            "How is the household connected to Mr. Bingley?"
        ]
    },

    {
        "id": "conversation_6",
        "questions": [
            "Who is Mr. Collins?",
            "What is his connection to the Bennet family?",
            "How does Elizabeth respond to his proposal?"
        ]
    },

    {
        "id": "conversation_7",
        "questions": [
            "Who is Charlotte Lucas?",
            "What is her relationship with Elizabeth?",
            "Why does her marriage become important to Elizabeth?"
        ]
    },

    {
        "id": "conversation_8",
        "questions": [
            "What kind of person is Lady Catherine?",
            "How does she treat Elizabeth?",
            "Why does she object to Elizabeth's relationship with Mr. Darcy?"
        ]
    },

    {
        "id": "conversation_9",
        "questions": [
            "What happens at the Netherfield ball?",
            "Who does Elizabeth dance with?",
            "How does Mr. Darcy behave toward her?"
        ]
    },

    {
        "id": "conversation_10",
        "questions": [
            "What role does Lydia Bennet play in the story?",
            "What problem does her relationship with Mr. Wickham create?",
            "How does this affect the Bennet family?"
        ]
    }
]


# ============================================================
# SEND REQUEST
# ============================================================

def send_message(session_id, question):

    response = requests.post(
        API_URL,
        json={
            "session_id": session_id,
            "question": question
        },
        timeout=180
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# RUN TESTS
# ============================================================

def run_tests():

    all_results = []

    print("=" * 70)
    print("DAY 20 - CONVERSATIONAL RAG MULTI-TURN TEST")
    print("=" * 70)

    for conversation in conversations:

        conversation_id = conversation["id"]

        session_id = f"day20_{conversation_id}"

        print("\n" + "=" * 70)
        print(conversation_id.upper())
        print("=" * 70)

        turns = []

        for turn_number, question in enumerate(
            conversation["questions"],
            start=1
        ):

            print("\n" + "-" * 60)
            print(f"TURN {turn_number}")
            print("-" * 60)

            print("Question:")
            print(question)

            try:

                result = send_message(
                    session_id,
                    question
                )

                print("\nRewritten question:")
                print(
                    result["rewritten_question"]
                )

                print("\nAnswer:")
                print(
                    result["answer"]
                )

                print("\nSources:")
                print(
                    result["sources"]
                )

                turn_result = {
                    "turn": turn_number,
                    "question": question,
                    "rewritten_question": result[
                        "rewritten_question"
                    ],
                    "answer": result["answer"],
                    "sources": result["sources"]
                }

            except Exception as error:

                print("\nERROR:")
                print(error)

                turn_result = {
                    "turn": turn_number,
                    "question": question,
                    "error": str(error)
                }

            turns.append(turn_result)

        all_results.append(
            {
                "conversation_id": conversation_id,
                "session_id": session_id,
                "turns": turns
            }
        )

    # ========================================================
    # SAVE RESULTS
    # ========================================================

    output_file = "conversation_test_results.json"

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_results,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\n" + "=" * 70)
    print("TESTING COMPLETE")
    print("=" * 70)

    print(
        f"\nResults saved to: {output_file}"
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    run_tests()