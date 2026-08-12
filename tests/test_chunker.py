from backend.app.ingestion.chunker import chunk_pages


def test_chunk_pages_preserves_metadata():
    pages = [
        {
            "page": 1,
            "text": "This is a test document. " * 100,
        }
    ]

    chunks = chunk_pages(
        pages=pages,
        doc_id="test-doc",
        source="test.pdf",
        title="Test Document",
    )

    assert len(chunks) > 0

    first_chunk = chunks[0]

    assert first_chunk["doc_id"] == "test-doc"
    assert first_chunk["source"] == "test.pdf"
    assert first_chunk["title"] == "Test Document"
    assert first_chunk["page"] == 1
    assert first_chunk["chunk_id"] == "test-doc-p1-c1"
    assert first_chunk["text"]


def test_chunk_pages_skips_empty_pages():
    pages = [
        {
            "page": 1,
            "text": "",
        },
        {
            "page": 2,
            "text": "This page contains useful content.",
        },
    ]

    chunks = chunk_pages(
        pages=pages,
        doc_id="test-doc",
        source="test.pdf",
        title="Test Document",
    )

    assert len(chunks) == 1
    assert chunks[0]["page"] == 2