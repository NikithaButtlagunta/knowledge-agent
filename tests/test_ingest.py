from unittest.mock import MagicMock, patch

from backend.app.ingestion.ingest import (
    calculate_file_hash,
    document_exists,
    get_document_info,
    load_registry,
    save_registry,
)


def test_calculate_file_hash(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello Knowledge Agent")

    first_hash = calculate_file_hash(str(test_file))
    second_hash = calculate_file_hash(str(test_file))

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_load_registry_when_file_does_not_exist(tmp_path):
    with patch(
        "backend.app.ingestion.ingest.REGISTRY_PATH",
        tmp_path / "registry.json",
    ):
        result = load_registry()

    assert result == []


def test_save_and_load_registry(tmp_path):
    registry_path = tmp_path / "registry.json"

    documents = [
        {
            "doc_id": "test-001",
            "source": "test.pdf",
            "title": "Test Document",
            "file_hash": "abc123",
            "chunks_created": 3,
        }
    ]

    with patch(
        "backend.app.ingestion.ingest.REGISTRY_PATH",
        registry_path,
    ):
        save_registry(documents)
        result = load_registry()

    assert result == documents


def test_document_exists():
    mock_registry = [
        {
            "doc_id": "doc-001",
            "source": "sample.pdf",
            "file_hash": "abc123",
        }
    ]

    with patch(
        "backend.app.ingestion.ingest.load_registry",
        return_value=mock_registry,
    ):
        result = document_exists("abc123")

    assert result is not None
    assert result["doc_id"] == "doc-001"


def test_document_does_not_exist():
    mock_registry = [
        {
            "doc_id": "doc-001",
            "source": "sample.pdf",
            "file_hash": "abc123",
        }
    ]

    with patch(
        "backend.app.ingestion.ingest.load_registry",
        return_value=mock_registry,
    ):
        result = document_exists("different-hash")

    assert result is None


def test_get_document_info():
    mock_registry = [
        {
            "doc_id": "doc-001",
            "source": "sample.pdf",
            "title": "Sample Document",
        }
    ]

    with patch(
        "backend.app.ingestion.ingest.load_registry",
        return_value=mock_registry,
    ):
        result = get_document_info("doc-001")

    assert result["doc_id"] == "doc-001"
    assert result["source"] == "sample.pdf"


def test_get_document_info_not_found():
    with patch(
        "backend.app.ingestion.ingest.load_registry",
        return_value=[],
    ):
        result = get_document_info("missing-doc")

    assert result is None


def test_ingest_pdf_success(tmp_path):
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_bytes(b"fake pdf content")

    mock_vector_store = MagicMock()

    fake_pages = [
        {
            "page": 1,
            "text": "This is sample document content.",
        }
    ]

    fake_chunks = [
        {
            "doc_id": "doc-001",
            "source": "sample.pdf",
            "title": "Sample Document",
            "page": 1,
            "chunk_id": "doc-001-p1-c1",
            "text": "This is sample document content.",
        }
    ]

    with patch(
        "backend.app.ingestion.ingest.document_exists",
        return_value=None,
    ), patch(
        "backend.app.ingestion.ingest.extract_text_from_pdf",
        return_value=fake_pages,
    ), patch(
        "backend.app.ingestion.ingest.chunk_pages",
        return_value=fake_chunks,
    ), patch(
        "backend.app.ingestion.ingest.get_vector_store",
        return_value=mock_vector_store,
    ), patch(
        "backend.app.ingestion.ingest.load_registry",
        return_value=[],
    ), patch(
        "backend.app.ingestion.ingest.save_registry",
    ) as mock_save_registry:

        from backend.app.ingestion.ingest import ingest_pdf

        result = ingest_pdf(
            pdf_path=str(pdf_file),
            doc_id="doc-001",
            source="sample.pdf",
            title="Sample Document",
        )

    assert result["success"] is True
    assert result["duplicate"] is False
    assert result["doc_id"] == "doc-001"
    assert result["chunks_created"] == 1

    mock_vector_store.add_documents.assert_called_once()

    mock_save_registry.assert_called_once()


def test_ingest_pdf_duplicate(tmp_path):
    pdf_file = tmp_path / "duplicate.pdf"
    pdf_file.write_bytes(b"duplicate pdf content")

    existing_document = {
        "doc_id": "existing-001",
        "source": "duplicate.pdf",
        "title": "Duplicate Document",
        "file_hash": "existing-hash",
    }

    with patch(
        "backend.app.ingestion.ingest.document_exists",
        return_value=existing_document,
    ):
        from backend.app.ingestion.ingest import ingest_pdf

        result = ingest_pdf(
            pdf_path=str(pdf_file),
            doc_id="new-001",
            source="duplicate.pdf",
            title="Duplicate Document",
        )

    assert result["success"] is False
    assert result["duplicate"] is True
    assert result["doc_id"] == "existing-001"
    assert result["chunks_created"] == 0