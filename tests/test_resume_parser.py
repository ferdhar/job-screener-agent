import io

import pytest
from docx import Document

from ui.resume_parser import (
    UnsupportedResumeFormat,
    extract_resume_text,
    extract_text_from_docx,
    extract_text_from_pdf,
    extract_text_from_txt,
)


def make_docx_bytes(paragraphs):
    document = Document()

    for paragraph in paragraphs:
        document.add_paragraph(paragraph)

    buffer = io.BytesIO()
    document.save(buffer)

    return buffer.getvalue()


class FakePdfPage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


class FakePdfReader:
    def __init__(self, _stream):
        self.pages = [
            FakePdfPage("Page one text"),
            FakePdfPage("Page two text"),
        ]


def test_extract_text_from_txt_decodes_utf8():
    data = "Line one\nLine two".encode("utf-8")

    assert extract_text_from_txt(data) == "Line one\nLine two"


def test_extract_text_from_docx_joins_paragraphs():
    data = make_docx_bytes(["Ferdinand Hartanto", "Python, Git, Linux"])

    text = extract_text_from_docx(data)

    assert "Ferdinand Hartanto" in text
    assert "Python, Git, Linux" in text


def test_extract_text_from_pdf_joins_pages(monkeypatch):
    monkeypatch.setattr("ui.resume_parser.PdfReader", FakePdfReader)

    text = extract_text_from_pdf(b"%PDF-1.4 fake bytes")

    assert "Page one text" in text
    assert "Page two text" in text


def test_extract_resume_text_dispatches_txt():
    data = "Resume text".encode("utf-8")

    assert extract_resume_text("resume.txt", data) == "Resume text"


def test_extract_resume_text_dispatches_pdf(monkeypatch):
    monkeypatch.setattr("ui.resume_parser.PdfReader", FakePdfReader)

    text = extract_resume_text("resume.pdf", b"%PDF-1.4 fake bytes")

    assert "Page one text" in text


def test_extract_resume_text_dispatches_docx():
    data = make_docx_bytes(["Some resume content"])

    text = extract_resume_text("resume.docx", data)

    assert "Some resume content" in text


def test_extract_resume_text_rejects_unsupported_extension():
    with pytest.raises(UnsupportedResumeFormat):
        extract_resume_text("resume.pages", b"data")


def test_extract_resume_text_rejects_empty_result():
    with pytest.raises(ValueError):
        extract_resume_text("resume.txt", b"   ")
