from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from backend.app.retrieval.retriever import search_documents


def test_search_documents_empty_query():
    result = search_documents("")

    assert result == []


def test_search_documents_returns_clean_results():
    mock_document = Document(
        page_content="Python is a programming language.",
        metadata={"page": 1},
    )

    mock_vector_store = MagicMock()

    mock_vector_store.similarity_search_with_score.return_value = [
        (mock_document, 0.25)
    ]

    with patch(
        "backend.app.retrieval.retriever.get_vector_store",
        return_value=mock_vector_store,
    ):
        results = search_documents("What is Python?")

    assert len(results) == 1

    document, score = results[0]

    assert document.page_content == "Python is a programming language."
    assert score == 0.25
    assert isinstance(score, float)


def test_search_documents_skips_empty_documents():
    empty_document = Document(
        page_content="",
        metadata={"page": 1},
    )

    valid_document = Document(
        page_content="Valid document content.",
        metadata={"page": 2},
    )

    mock_vector_store = MagicMock()

    mock_vector_store.similarity_search_with_score.return_value = [
        (empty_document, 0.10),
        (valid_document, 0.20),
    ]

    with patch(
        "backend.app.retrieval.retriever.get_vector_store",
        return_value=mock_vector_store,
    ):
        results = search_documents("test query")

    assert len(results) == 1
    assert results[0][0].page_content == "Valid document content."


def test_search_documents_handles_errors():
    mock_vector_store = MagicMock()

    mock_vector_store.similarity_search_with_score.side_effect = Exception(
        "Test retrieval error"
    )

    with patch(
        "backend.app.retrieval.retriever.get_vector_store",
        return_value=mock_vector_store,
    ):
        results = search_documents("test query")

    assert results == []