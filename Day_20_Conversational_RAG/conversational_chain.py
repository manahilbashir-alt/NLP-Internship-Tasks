from pathlib import Path

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage

from langchain_retriever import create_compression_retriever


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ENV_FILE = (
    BASE_DIR.parent
    / "Day_18_RAG_Retrieval_Generation"
    / ".env"
)

load_dotenv(ENV_FILE)

TOP_K = 4


# ============================================================
# LLM
# ============================================================

def create_llm():

    return ChatGoogleGenerativeAI(
        model="gemini-flash-lite-latest",
        temperature=0
    )


# ============================================================
# RESPONSE TEXT EXTRACTION
# ============================================================

def get_response_text(response):

    content = response.content

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):

        text_parts = []

        for item in content:

            if isinstance(item, str):
                text_parts.append(item)

            elif isinstance(item, dict):

                text = item.get("text")

                if text:
                    text_parts.append(text)

        return " ".join(text_parts).strip()

    return str(content).strip()


# ============================================================
# HISTORY FORMATTING
# ============================================================

def format_history(history):

    if not history:
        return "No previous conversation."

    history_parts = []

    for message in history:

        if isinstance(message, HumanMessage):

            history_parts.append(
                f"User: {message.content}"
            )

        elif isinstance(message, AIMessage):

            history_parts.append(
                f"Assistant: {message.content}"
            )

    return "\n".join(history_parts)


# ============================================================
# QUESTION REWRITING
# ============================================================

def make_standalone_question(question, history):

    if not history:
        return question

    llm = create_llm()

    history_text = format_history(history)

    prompt = f"""
You are a question rewriting assistant.

Convert the user's latest question into a standalone question.

Use the conversation history to resolve references such as:

- he
- she
- it
- they
- his
- her
- this
- that
- the previous point
- the second point
- the above topic

Do not answer the question.

Only return the rewritten standalone question.

Conversation history:
{history_text}

Latest user question:
{question}

Standalone question:
"""

    response = llm.invoke(prompt)

    rewritten_question = get_response_text(response)

    if not rewritten_question:
        return question

    return rewritten_question


# ============================================================
# SOURCE FORMATTING
# ============================================================

def format_sources(documents):

    if not documents:
        return "No source information available."

    sources = []

    for document in documents:

        filename = document.metadata.get(
            "source_filename",
            "Unknown document"
        )

        page = document.metadata.get(
            "page_number",
            "Unknown page"
        )

        chunk = document.metadata.get(
            "chunk_index",
            "Unknown chunk"
        )

        source = (
            f"{filename}, page {page}, chunk {chunk}"
        )

        if source not in sources:
            sources.append(source)

    return "\n".join(
        f"- {source}"
        for source in sources
    )


# ============================================================
# DOCUMENT RETRIEVAL
# ============================================================

def retrieve_documents(question):

    retriever = create_compression_retriever(
        top_k=TOP_K
    )

    documents = retriever.invoke(
        question
    )

    return documents


# ============================================================
# CONTEXT BUILDING
# ============================================================

def build_context(documents):

    if not documents:
        return (
            "No relevant documents were retrieved "
            "from the knowledge base."
        )

    context_parts = []

    for index, document in enumerate(
        documents,
        start=1
    ):

        filename = document.metadata.get(
            "source_filename",
            "Unknown document"
        )

        page = document.metadata.get(
            "page_number",
            "Unknown page"
        )

        chunk = document.metadata.get(
            "chunk_index",
            "Unknown chunk"
        )

        context_parts.append(
            f"""
Document {index}

Source filename: {filename}
Page number: {page}
Chunk index: {chunk}

Content:
{document.page_content}
"""
        )

    return "\n".join(context_parts)


# ============================================================
# ANSWER GENERATION
# ============================================================

def generate_answer(
    question,
    history,
    documents
):

    llm = create_llm()

    history_text = format_history(history)

    context = build_context(documents)

    prompt = f"""
You are a document-based question-answering assistant.

Answer the user's question using the retrieved document
context and conversation history.

Conversation history:
{history_text}

Retrieved document context:
{context}

Rules:

1. Use the retrieved document context as the main source.

2. Use conversation history only to understand references
   and conversational context.

3. Do not invent information.

4. If the retrieved documents do not contain enough information,
   say that the information is not available in the provided
   documents.

5. Give a clear and concise answer.

6. Do not include a separate source list in your answer.
   The application adds source information separately.

User question:
{question}

Answer:
"""

    response = llm.invoke(prompt)

    answer = get_response_text(response)

    if not answer:

        answer = (
            "I could not generate an answer from the "
            "retrieved documents."
        )

    return answer


# ============================================================
# COMPLETE CONVERSATIONAL RAG
# ============================================================

def chat(question, history=None):

    if history is None:
        history = []

    # Step 1: Convert follow-up into standalone question
    standalone_question = make_standalone_question(
        question,
        history
    )

    # Step 2: Retrieve compressed documents
    documents = retrieve_documents(
        standalone_question
    )

    # Step 3: Generate answer
    answer = generate_answer(
        standalone_question,
        history,
        documents
    )

    # Step 4: Create source citation
    sources = format_sources(
        documents
    )

    # Step 5: Update conversation history
    updated_history = history.copy()

    updated_history.append(
        HumanMessage(
            content=question
        )
    )

    updated_history.append(
        AIMessage(
            content=answer
        )
    )

    return {
        "answer": answer,
        "sources": sources,
        "rewritten_question": standalone_question,
        "history": updated_history
    }


# ============================================================
# LOCAL CONVERSATIONAL RAG TEST
# ============================================================

if __name__ == "__main__":

    conversation = []

    # --------------------------------------------------------
    # FIRST TURN
    # --------------------------------------------------------

    first_question = "Who is Mr. Darcy?"

    result = chat(
        first_question,
        conversation
    )

    print("\n" + "=" * 70)
    print("FIRST TURN")
    print("=" * 70)

    print("\nQUESTION:")
    print(first_question)

    print("\nREWRITTEN QUESTION:")
    print(result["rewritten_question"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    print(result["sources"])

    conversation = result["history"]

    # --------------------------------------------------------
    # SECOND TURN
    # --------------------------------------------------------

    second_question = (
        "What about his relationship with Elizabeth?"
    )

    result = chat(
        second_question,
        conversation
    )

    print("\n" + "=" * 70)
    print("SECOND TURN - FOLLOW-UP")
    print("=" * 70)

    print("\nQUESTION:")
    print(second_question)

    print("\nREWRITTEN QUESTION:")
    print(result["rewritten_question"])

    print("\nANSWER:")
    print(result["answer"])

    print("\nSOURCES:")
    print(result["sources"])