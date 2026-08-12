from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_pages(
    pages: list[dict],
    doc_id: str,
    source: str,
    title: str,
) -> list[dict]:
    """
    Split extracted PDF pages into smaller chunks
    while preserving page-level metadata.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )

    chunks = []

    for page in pages:
        page_number = page["page"]
        text = page["text"]

        if not text.strip():
            continue

        page_chunks = splitter.split_text(text)

        for chunk_index, chunk_text in enumerate(page_chunks, start=1):
            chunks.append(
                {
                    "doc_id": doc_id,
                    "source": source,
                    "title": title,
                    "page": page_number,
                    "chunk_id": f"{doc_id}-p{page_number}-c{chunk_index}",
                    "text": chunk_text,
                }
            )

    return chunks



if __name__ == "__main__":
    from backend.app.ingestion.pdf_loader import extract_text_from_pdf

    pdf_file = "data/Sample.pdf"

    pages = extract_text_from_pdf(pdf_file)

    chunks = chunk_pages(
        pages=pages,
        doc_id="Sample",
        source="Sample.pdf",
        title="Sample Document",
    )

    print(f"Total chunks: {len(chunks)}")

    for chunk in chunks[:3]:
        print("\n--- Chunk ---")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Page: {chunk['page']}")
        print(f"Source: {chunk['source']}")
        print(f"Text: {chunk['text'][:300]}")