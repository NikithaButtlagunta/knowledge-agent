from unittest.mock import MagicMock, patch

from langchain_core.documents import Document

from backend.app.retrieval.vector_store import (
    get_vector_store,
    search_documents,
)


def test_get_vector_store_creates_chroma_store():
    mock_embedding_model = MagicMock()

    with patch(
        "backend.app.retrieval.vector_store.get_embedding_model",
        return_value=mock_embedding_model,
    ), patch(
        "backend.app.retrieval.vector_store.Chroma"
    ) as mock_chroma:

        get_vector_store()

    mock_chroma.assert_called_once()

    call_kwargs = mock_chroma.call_args.kwargs

    assert call_kwargs["collection_name"] == "knowledge_agent"
    assert call_kwargs["embedding_function"] == mock_embedding_model
    assert "chroma_db" in call_kwargs["persist_directory"]


def test_search_documents_returns_results():
    mock_document = Document(
        page_content="Python is a programming language.",
        metadata={
            "source": "test.pdf",
            "page": 1,
            "chunk_id": "test-p1-c1",
        },
    )

    mock_vector_store = MagicMock()

    mock_vector_store.similarity_search_with_score.return_value = [
        (mock_document, 0.15)
    ]

    with patch(
        "backend.app.retrieval.vector_store.get_vector_store",
        return_value=mock_vector_store,
    ):
        results = search_documents("What is Python?", k=5)

    assert len(results) == 1

    document, score = results[0]

    assert document.page_content == "Python is a programming language."
    assert score == 0.15

    mock_vector_store.similarity_search_with_score.assert_called_once_with(
        "What is Python?",
        k=5,
    )