import json
import time
from pathlib import Path

from conversation_rag import ConversationalRAG


# ============================================================
# CONFIGURATION
# ============================================================

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output"

OUTPUT_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# 10 MULTI-TURN CONVERSATIONS
# ============================================================

CONVERSATIONS = [

    {
        "id": 1,
        "topic": "ChromaDB",
        "turns": [
            "What is ChromaDB?",
            "What about the second point?",
            "Why is it useful in RAG?"
        ]
    },

    {
        "id": 2,
        "topic": "Embeddings",
        "turns": [
            "What are embeddings?",
            "How are they used in retrieval?",
            "What about the previous concept?"
        ]
    },

    {
        "id": 3,
        "topic": "Vector databases",
        "turns": [
            "What is a vector database?",
            "How does it help RAG?",
            "What about similarity search?"
        ]
    },

    {
        "id": 4,
        "topic": "Similarity search",
        "turns": [
            "What is similarity search?",
            "What does it compare?",
            "Why is that important?"
        ]
    },

    {
        "id": 5,
        "topic": "RAG",
        "turns": [
            "What is RAG?",
            "What is the retrieval part?",
            "What happens after retrieval?"
        ]
    },

    {
        "id": 6,
        "topic": "Embeddings and queries",
        "turns": [
            "How is a user question converted for retrieval?",
            "What is compared with it?",
            "Why are embeddings needed?"
        ]
    },

    {
        "id": 7,
        "topic": "Vector retrieval",
        "turns": [
            "How does vector retrieval work?",
            "What happens to the query?",
            "What about the stored documents?"
        ]
    },

    {
        "id": 8,
        "topic": "ChromaDB and RAG",
        "turns": [
            "How can ChromaDB be used in RAG?",
            "What does it store?",
            "How does retrieval happen?"
        ]
    },

    {
        "id": 9,
        "topic": "Document chunks",
        "turns": [
            "Why do RAG systems use document chunks?",
            "How are chunks retrieved?",
            "What about embeddings?"
        ]
    },

    {
        "id": 10,
        "topic": "Independent question after context",
        "turns": [
            "What is ChromaDB?",
            "What is similarity search?",
            "Tell me about embeddings."
        ]
    }
]


# ============================================================
# HELPER: CHECK MEMORY EFFECT
# ============================================================

def evaluate_memory_effect(
    question,
    contextualized_question,
    turn_number
):

    question_lower = question.lower()

    contextualized_lower = (
        contextualized_question.lower()
    )

    # --------------------------------------------------------
    # Follow-up indicators
    # --------------------------------------------------------

    follow_up_words = [
        "what about",
        "why",
        "how",
        "it",
        "they",
        "them",
        "this",
        "that",
        "these",
        "those",
        "previous",
        "second",
        "first",
        "third",
        "more",
    ]

    is_follow_up = any(
        word in question_lower
        for word in follow_up_words
    )

    # --------------------------------------------------------
    # Memory successfully added context
    # --------------------------------------------------------

    memory_added_context = (
        contextualized_question
        != question
    )

    # --------------------------------------------------------
    # Determine effect
    # --------------------------------------------------------

    if turn_number == 1:

        return {
            "effect": "baseline",
            "reason": (
                "First turn has no previous "
                "conversation history."
            )
        }

    if (
        is_follow_up
        and memory_added_context
    ):

        return {
            "effect": "helped",
            "reason": (
                "Session memory added previous "
                "conversation context to the "
                "follow-up question."
            )
        }

    if (
        not is_follow_up
        and memory_added_context
    ):

        return {
            "effect": "possible_noise",
            "reason": (
                "The question appears independent, "
                "but previous conversation context "
                "was added."
            )
        }

    return {
        "effect": "neutral",
        "reason": (
            "Memory did not change the question."
        )
    }


# ============================================================
# RUN ONE CONVERSATION
# ============================================================

def run_conversation(
    rag,
    conversation
):

    session_id = (
        f"evaluation_session_"
        f"{conversation['id']}"
    )

    results = []

    for turn_number, question in enumerate(
        conversation["turns"],
        start=1
    ):

        print()
        print(
            f"Session {conversation['id']} "
            f"| Turn {turn_number}"
        )

        print(
            f"Question: {question}"
        )

        start_time = time.perf_counter()

        result = rag.chat(
            session_id=session_id,
            question=question
        )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        contextualized_question = result[
            "contextualized_question"
        ]

        sources = result[
            "sources"
        ]

        memory_effect = (
            evaluate_memory_effect(
                question,
                contextualized_question,
                turn_number
            )
        )

        print(
            "Contextualized:",
            contextualized_question
        )

        print(
            "Sources:",
            sources
        )

        print(
            "Memory effect:",
            memory_effect["effect"]
        )

        results.append(
            {
                "turn": turn_number,
                "question": question,
                "contextualized_question":
                    contextualized_question,
                "answer": result["answer"],
                "sources": sources,
                "history_length":
                    result["history_length"],
                "retrieval_time_seconds":
                    round(elapsed, 4),
                "memory_effect":
                    memory_effect["effect"],
                "memory_reason":
                    memory_effect["reason"],
            }
        )

    return {
        "conversation_id":
            conversation["id"],

        "topic":
            conversation["topic"],

        "session_id":
            session_id,

        "turns":
            results
    }


# ============================================================
# MAIN EVALUATION
# ============================================================

def main():

    print("=" * 80)

    print(
        "DAY 20 - 10 MULTI-TURN "
        "CONVERSATIONAL RAG EVALUATION"
    )

    print("=" * 80)

    # --------------------------------------------------------
    # Create RAG system
    # --------------------------------------------------------

    rag = ConversationalRAG()

    all_results = []

    # --------------------------------------------------------
    # Run all conversations
    # --------------------------------------------------------

    for conversation in CONVERSATIONS:

        print()
        print("#" * 80)

        print(
            f"CONVERSATION "
            f"{conversation['id']}: "
            f"{conversation['topic']}"
        )

        print("#" * 80)

        result = run_conversation(
            rag,
            conversation
        )

        all_results.append(
            result
        )

    # --------------------------------------------------------
    # Calculate statistics
    # --------------------------------------------------------

    total_turns = 0

    helped = 0

    possible_noise = 0

    neutral = 0

    baseline = 0

    for conversation in all_results:

        for turn in conversation[
            "turns"
        ]:

            total_turns += 1

            effect = turn[
                "memory_effect"
            ]

            if effect == "helped":
                helped += 1

            elif effect == "possible_noise":
                possible_noise += 1

            elif effect == "neutral":
                neutral += 1

            elif effect == "baseline":
                baseline += 1

    # --------------------------------------------------------
    # Evaluation summary
    # --------------------------------------------------------

    summary = {

        "total_conversations":
            len(all_results),

        "turns_per_conversation":
            3,

        "total_turns":
            total_turns,

        "memory_helped":
            helped,

        "possible_memory_noise":
            possible_noise,

        "neutral":
            neutral,

        "baseline":
            baseline,
    }

    # --------------------------------------------------------
    # Complete report
    # --------------------------------------------------------

    report = {

        "project":
            "Day 20 Conversational RAG",

        "evaluation":
            "10 multi-turn conversations",

        "summary":
            summary,

        "conversations":
            all_results
    }

    # --------------------------------------------------------
    # Save JSON
    # --------------------------------------------------------

    json_path = (
        OUTPUT_DIR
        / "conversation_evaluation.json"
    )

    with open(
        json_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    # --------------------------------------------------------
    # Create Markdown report
    # --------------------------------------------------------

    md_path = (
        OUTPUT_DIR
        / "conversation_evaluation.md"
    )

    with open(
        md_path,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "# Day 20 - Conversational RAG Evaluation\n\n"
        )

        file.write(
            "## Objective\n\n"
        )

        file.write(
            "Test 10 multi-turn conversations and "
            "document where session memory helps "
            "retrieval quality and where it introduces "
            "noise.\n\n"
        )

        file.write(
            "## Summary\n\n"
        )

        file.write(
            f"- Total conversations: "
            f"{summary['total_conversations']}\n"
        )

        file.write(
            f"- Total turns: "
            f"{summary['total_turns']}\n"
        )

        file.write(
            f"- Memory helped: "
            f"{summary['memory_helped']}\n"
        )

        file.write(
            f"- Possible memory noise: "
            f"{summary['possible_memory_noise']}\n"
        )

        file.write(
            f"- Neutral: "
            f"{summary['neutral']}\n"
        )

        file.write(
            f"- Baseline turns: "
            f"{summary['baseline']}\n\n"
        )

        file.write(
            "## Conversation Results\n\n"
        )

        for conversation in all_results:

            file.write(
                f"### Conversation "
                f"{conversation['conversation_id']}: "
                f"{conversation['topic']}\n\n"
            )

            file.write(
                "| Turn | Question | "
                "Contextualized Question | "
                "Memory Effect | Sources |\n"
            )

            file.write(
                "|---|---|---|---|---|\n"
            )

            for turn in conversation[
                "turns"
            ]:

                sources_text = "; ".join(
                    f"{source['filename']} "
                    f"(Page {source['page']})"
                    for source
                    in turn["sources"]
                )

                file.write(
                    f"| {turn['turn']} | "
                    f"{turn['question']} | "
                    f"{turn['contextualized_question']} | "
                    f"{turn['memory_effect']} | "
                    f"{sources_text} |\n"
                )

            file.write("\n")

        file.write(
            "## Findings\n\n"
        )

        file.write(
            "### Where session memory helps\n\n"
        )

        file.write(
            "- Follow-up questions such as "
            "\"What about the second point?\" "
            "can be contextualized using the "
            "previous user question.\n"
        )

        file.write(
            "- Pronoun-based questions such as "
            "\"Why is it useful?\" can retain "
            "the previous conversational topic.\n"
        )

        file.write(
            "- Session history allows retrieval "
            "to receive a more complete query "
            "instead of an ambiguous follow-up.\n\n"
        )

        file.write(
            "### Where session memory can introduce noise\n\n"
        )

        file.write(
            "- Independent questions may not need "
            "previous conversation context.\n"
        )

        file.write(
            "- Automatically adding previous context "
            "to an independent question can make "
            "the retrieval query unnecessarily longer.\n"
        )

        file.write(
            "- Long conversation histories can "
            "eventually introduce unrelated "
            "information if memory is not managed.\n\n"
        )

        file.write(
            "## Conclusion\n\n"
        )

        file.write(
            "Session memory improves conversational "
            "RAG when the user asks follow-up "
            "questions that depend on previous turns. "
            "However, memory should be applied "
            "selectively because unrelated questions "
            "can introduce unnecessary context and "
            "retrieval noise.\n"
        )

    # --------------------------------------------------------
    # Print final summary
    # --------------------------------------------------------

    print()
    print("=" * 80)

    print(
        "EVALUATION COMPLETE"
    )

    print("=" * 80)

    print(
        f"Conversations tested: "
        f"{summary['total_conversations']}"
    )

    print(
        f"Total turns: "
        f"{summary['total_turns']}"
    )

    print(
        f"Memory helped: "
        f"{summary['memory_helped']}"
    )

    print(
        f"Possible memory noise: "
        f"{summary['possible_memory_noise']}"
    )

    print(
        f"Neutral: "
        f"{summary['neutral']}"
    )

    print(
        f"Baseline: "
        f"{summary['baseline']}"
    )

    print()
    print(
        f"JSON report: {json_path}"
    )

    print(
        f"Markdown report: {md_path}"
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()