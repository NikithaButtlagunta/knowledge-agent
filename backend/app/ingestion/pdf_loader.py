from pathlib import Path

from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """
    Extract text from every page of a PDF.

    Returns:
        A list of dictionaries containing:
        - page number
        - extracted text
    """

    pdf_path = Path(file_path)

    reader = PdfReader(pdf_path)

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append(
            {
                "page": page_number,
                "text": text.strip(),
            }
        )

    return pages


if __name__ == "__main__":
    pdf_file = "data/sample.pdf"

    pages = extract_text_from_pdf(pdf_file)

    for page in pages:
        print(f"\n--- Page {page['page']} ---")
        print(page["text"][:500])