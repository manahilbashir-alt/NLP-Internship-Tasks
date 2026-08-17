def build_augmented_prompt(query, results):
    """
    Build a structured prompt using retrieved chunks.
    """

    context_parts = []

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    for i, document in enumerate(documents):

        metadata = metadatas[i]

        source = metadata.get(
            "source",
            "Unknown"
        )

        chunk_id = metadata.get(
            "chunk_id",
            "Unknown"
        )

        context_parts.append(
            f"""
[Source: {source} | Chunk: {chunk_id}]

{document}
"""
        )

    context = "\n".join(context_parts)

    prompt = f"""
You are a grounded question-answering assistant.

Your task is to answer the user's question using ONLY the
information provided in the retrieved context.

Do not use outside knowledge.

If the answer cannot be found in the context, clearly say:

"I could not find the answer in the provided documents."

Always mention the source document used for the answer.

--------------------
RETRIEVED CONTEXT
--------------------

{context}

--------------------
USER QUESTION
--------------------

{query}

--------------------
ANSWER INSTRUCTIONS
--------------------

1. Answer the question clearly and concisely.
2. Use only the retrieved context.
3. Do not invent information.
4. Mention the source document.
5. If the context does not contain the answer, say so.
"""

    return prompt


def format_sources(results):
    """
    Extract unique source references from retrieval results.
    """

    sources = []

    metadatas = results["metadatas"][0]

    for metadata in metadatas:

        source = metadata.get(
            "source",
            "Unknown"
        )

        chunk_id = metadata.get(
            "chunk_id",
            "Unknown"
        )

        reference = (
            f"{source} "
            f"(chunk {chunk_id})"
        )

        if reference not in sources:
            sources.append(reference)

    return sources