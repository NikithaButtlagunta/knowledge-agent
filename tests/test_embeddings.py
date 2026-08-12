from unittest.mock import MagicMock, patch

from backend.app.retrieval.embeddings import get_embedding_model


def test_get_embedding_model():
    mock_embeddings = MagicMock()

    with patch(
        "backend.app.retrieval.embeddings.HuggingFaceEmbeddings",
        return_value=mock_embeddings,
    ) as mock_class:

        result = get_embedding_model()

    assert result == mock_embeddings

    mock_class.assert_called_once_with(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )