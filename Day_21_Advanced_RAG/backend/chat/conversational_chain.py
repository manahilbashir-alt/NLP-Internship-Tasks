import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()   # will look for .env in backend/ — see note below
import re
from retrieval.hybrid_retriever import get_hybrid_retriever as get_langchain_retriever
from langchain_google_genai import ChatGoogleGenerativeAI

retriever = get_langchain_retriever(k=6)
llm = ChatGoogleGenerativeAI(model="gemini-flash-lite-latest")

def format_sources(docs):
    """Turns retrieved chunks into a readable 'Sources:' list, showing
    each unique (file, page) combination only once."""
    seen = set()
    lines = []
    for doc in docs:
        source_file = doc.metadata.get("source_file", "unknown file")
        page_no = doc.metadata.get("page_no", "unknown page")
        key = (source_file, page_no)
        if key not in seen:
            seen.add(key)
            lines.append(f"- {source_file}, page {page_no}")
    return "\n".join(lines)

def get_text(response):
    """Gemini sometimes returns response.content as a string, sometimes as
    a list of parts. This handles both cases safely."""
    content = response.content
    if isinstance(content, list):
        content = "".join(
            part if isinstance(part, str) else part.get("text", "")
            for part in content
        )
    return content.strip()


def rewrite_question(question, chat_history):
    """Turns a follow-up like 'what about its disadvantages?' into a
    standalone question, using the conversation so far."""
    if not chat_history:
        return None # nothing to rewrite on the first question

    history_text = "\n".join(
        f"{role}: {text}" for role, text in chat_history
    )
    prompt = (
        "Given this conversation so far:\n"
        f"{history_text}\n\n"
        f"Rewrite this follow-up question so it can be understood on its own, "
        f"without needing the conversation above. Only output the rewritten "
        f"question, nothing else.\n\n"
        f"Follow-up question: {question}\n"
        f"Standalone question:"
    )
    response = llm.invoke(prompt)
    return get_text(response)


def answer_question(standalone_question, chat_history):
    docs = retriever.invoke(standalone_question)
    context = "\n\n".join(doc.page_content for doc in docs)

    # Pull out any figure images among the retrieved chunks
    image_paths = []
    for doc in docs:
        if doc.metadata.get("chunk_type") == "image":
            match = re.search(r"\((images/[^)]+)\)", doc.page_content)
            if match:
                image_paths.append(match.group(1))

    history_text = "\n".join(f"{role}: {text}" for role, text in chat_history)
    prompt = (
        f"Answer the question using ONLY the context below. If the answer "
        f"isn't in the context, say you don't know.\n\n"
        f"Context:\n{context}\n\n"
        f"Conversation so far:\n{history_text}\n\n"
        f"Question: {standalone_question}\n"
        f"Answer:"
    )
    response = llm.invoke(prompt)
    answer = get_text(response)
    sources = format_sources(docs)
    return answer, sources, image_paths


def chat(question, chat_history):
    standalone_question = rewrite_question(question, chat_history)
    if not standalone_question:
        standalone_question = question
    answer, sources, images = answer_question(standalone_question, chat_history)
    chat_history.append(("Human", question))
    chat_history.append(("AI", answer))
    return answer, sources, chat_history, standalone_question, images

if __name__ == "__main__":
    history = []

    q1 = "What is SVM?"
    a1, sources1, history, _ = chat(q1, history)
    print(f"Q1: {q1}\nA1: {a1}\nSources:\n{sources1}\n")

    q2 = "What are its disadvantages?"
    a2, sources2, history, rewritten = chat(q2, history)
    print(f"Q2 (original): {q2}")
    print(f"Q2 (rewritten): {rewritten}")
    print(f"A2: {a2}\nSources:\n{sources2}\n")