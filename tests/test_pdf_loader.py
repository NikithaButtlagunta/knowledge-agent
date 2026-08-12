from pathlib import Path

from pypdf import PdfWriter

from backend.app.ingestion.pdf_loader import extract_text_from_pdf


def test_extract_text_from_pdf(tmp_path: Path):
    pdf_path = tmp_path / "test.pdf"

    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)

    with open(pdf_path, "wb") as pdf_file:
        writer.write(pdf_file)

    pages = extract_text_from_pdf(str(pdf_path))

    assert isinstance(pages, list)
    assert len(pages) == 1
    assert pages[0]["page"] == 1
    assert "text" in pages[0]