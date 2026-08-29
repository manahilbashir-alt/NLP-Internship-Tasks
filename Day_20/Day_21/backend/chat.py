import os
from typing import Dict, List

from dotenv import load_dotenv
from google import genai

from rag import collection, embedding_model


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# SESSION MEMORY
# ============================================================

sessions: Dict[str, List[dict]] = {}


# ============================================================
# GEMINI CLIENT
# ============================================================

API_KEY = os.getenv("GEMINI_API_KEY")

client = None

if API_KEY:
    client = genai.Client(
        api_key=API_KEY
    )


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_chunks(
    question: str,
    top_k: int = 3
):
    """
    Retrieve the most relevant chunks from ChromaDB.
    """

    query_embedding = embedding_model.encode(
        [question],
        normalize_embeddings=True
    ).tolist()[0]

    count = collection.count()

    if count == 0:
        return []

    top_k = min(
        top_k,
        count
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    retrieved = []

    for document, metadata, distance in zip(
        documents,
        metadatas,
        distances
    ):

        retrieved.append(
            {
                "content": document,

                "source": metadata.get(
                    "source",
                    "unknown"
                ),

                "chunk_id": metadata.get(
                    "chunk_id"
                ),

                "distance": round(
                    float(distance),
                    4
                )
            }
        )

    return retrieved


# ============================================================
# SESSION FUNCTIONS
# ============================================================

def get_session_history(
    session_id: str
):
    """
    Return conversation history for a session.
    """

    return sessions.get(
        session_id,
        []
    )


def save_message(
    session_id: str,
    role: str,
    content: str
):
    """
    Save a message to session memory.
    """

    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append(
        {
            "role": role,
            "content": content
        }
    )


# ============================================================
# LLM RESPONSE
# ============================================================

def generate_answer(
    question: str,
    retrieved_chunks: list,
    history: list
):
    """
    Generate a grounded answer using Gemini 3.6 Flash
    through the Gemini Interactions API.
    """

    # --------------------------------------------------------
    # No relevant chunks
    # --------------------------------------------------------

    if not retrieved_chunks:

        return (
            "I could not find relevant information "
            "in the uploaded documents."
        )

    # --------------------------------------------------------
    # Build document context
    # --------------------------------------------------------

    context_parts = []

    for i, chunk in enumerate(
        retrieved_chunks,
        start=1
    ):

        context_parts.append(
            f"""
SOURCE {i}
File: {chunk['source']}
Chunk ID: {chunk['chunk_id']}

Content:
{chunk['content']}
"""
        )

    context = "\n".join(
        context_parts
    )

    # --------------------------------------------------------
    # Build conversation history
    # --------------------------------------------------------

    history_text = ""

    if history:

        recent_history = history[-6:]

        history_parts = []

        for message in recent_history:

            history_parts.append(
                f"{message['role'].upper()}: "
                f"{message['content']}"
            )

        history_text = "\n".join(
            history_parts
        )

    # --------------------------------------------------------
    # System instruction
    # --------------------------------------------------------

    system_instruction = """
You are a helpful document question-answering assistant.

Answer the user's question ONLY using the information
contained in the provided document context.

Rules:

1. Do not invent facts.

2. If the answer is not present in the context,
   clearly say that the information is not available
   in the uploaded documents.

3. Keep the answer clear and concise.

4. Use conversation history when it helps understand
   follow-up questions.

5. Do not use outside knowledge.

6. Do not browse the internet.

7. Prefer information from the retrieved document chunks.
"""

    # --------------------------------------------------------
    # User input
    # --------------------------------------------------------

    user_input = f"""
CONVERSATION HISTORY:

{history_text}

DOCUMENT CONTEXT:

{context}

USER QUESTION:

{question}

Answer the question using ONLY the document context.
"""

    # --------------------------------------------------------
    # Check Gemini configuration
    # --------------------------------------------------------

    if client is None:

        return (
            "Gemini API key is not configured. "
            "However, relevant document chunks were "
            "successfully retrieved. Please configure "
            "GEMINI_API_KEY to generate the final answer."
        )

    # --------------------------------------------------------
    # Generate response using Interactions API
    # --------------------------------------------------------

    try:

        interaction = client.interactions.create(
            model="gemini-3.6-flash",
            system_instruction=system_instruction,
            input=user_input
        )

        return interaction.output_text

    except Exception as e:

        return (
            f"Gemini API error: {str(e)}"
        )


# ============================================================
# COMPLETE CHAT FUNCTION
# ============================================================

def chat_with_rag(
    session_id: str,
    question: str,
    top_k: int = 3
):
    """
    Complete conversational RAG pipeline.

    Flow:

    User Question
          ↓
    Session History
          ↓
    Query Embedding
          ↓
    ChromaDB Retrieval
          ↓
    Relevant Chunks
          ↓
    Gemini 3.6 Flash
          ↓
    Grounded Answer
          ↓
    Session Memory
    """

    # --------------------------------------------------------
    # Get previous conversation
    # --------------------------------------------------------

    history = get_session_history(
        session_id
    )

    # --------------------------------------------------------
    # Retrieve relevant chunks
    # --------------------------------------------------------

    retrieved_chunks = retrieve_chunks(
        question,
        top_k=top_k
    )

    # --------------------------------------------------------
    # Generate grounded answer
    # --------------------------------------------------------

    answer = generate_answer(
        question,
        retrieved_chunks,
        history
    )

    # --------------------------------------------------------
    # Save user message
    # --------------------------------------------------------

    save_message(
        session_id,
        "user",
        question
    )

    # --------------------------------------------------------
    # Save assistant response
    # --------------------------------------------------------

    save_message(
        session_id,
        "assistant",
        answer
    )

    # --------------------------------------------------------
    # Return response
    # --------------------------------------------------------

    return {
        "session_id": session_id,

        "question": question,

        "answer": answer,

        "sources": retrieved_chunks,

        "conversation_length": len(
            get_session_history(
                session_id
            )
        )
    }