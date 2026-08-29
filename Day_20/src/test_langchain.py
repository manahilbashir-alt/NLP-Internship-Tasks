from langchain_retriever import (
    load_documents,
    create_chunks,
    build_langchain_retriever,
    retrieve
)


def test_langchain_retriever():

    documents = load_documents()

    assert len(documents) > 0

    chunks = create_chunks(documents)

    assert len(chunks) > 0

    retriever = build_langchain_retriever(chunks)

    assert retriever is not None

    query = "What is ChromaDB?"

    results, elapsed = retrieve(
        query,
        retriever
    )

    assert elapsed >= 0
    assert len(results) > 0

    for result in results:

        assert "rank" in result
        assert "source" in result
        assert "chunk_id" in result
        assert "text" in result


def test_langchain_retriever_returns_documents():

    documents = load_documents()

    chunks = create_chunks(documents)

    retriever = build_langchain_retriever(chunks)

    results, _ = retrieve(
        "What are embeddings?",
        retriever
    )

    assert isinstance(results, list)
    assert len(results) > 0