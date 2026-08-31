import io

from docx import Document
from pypdf import PdfReader


class UnsupportedResumeFormat(Exception):
    """Raised when an uploaded resume file type is not supported."""


def extract_text_from_txt(data: bytes) -> str:
    return data.decode("utf-8", errors="ignore").strip()


def extract_text_from_pdf(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))

    pages = [page.extract_text() or "" for page in reader.pages]

    return "\n".join(pages).strip()


def extract_text_from_docx(data: bytes) -> str:
    document = Document(io.BytesIO(data))

    paragraphs = [paragraph.text for paragraph in document.paragraphs]

    return "\n".join(paragraphs).strip()


EXTRACTORS_BY_EXTENSION = {
    "txt": extract_text_from_txt,
    "pdf": extract_text_from_pdf,
    "docx": extract_text_from_docx,
}


def extract_resume_text(filename: str, data: bytes) -> str:
    """
    Extract resume text from uploaded file bytes based on file extension.
    """

    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    extractor = EXTRACTORS_BY_EXTENSION.get(extension)

    if extractor is None:
        raise UnsupportedResumeFormat(
            f"Unsupported resume file type: .{extension or filename}. "
            "Please upload a PDF, DOCX, or TXT file."
        )

    text = extractor(data)

    if not text:
        raise ValueError(
            "No text could be extracted from the uploaded resume."
        )

    return text
