import io
import re
import logging

logger = logging.getLogger(__name__)


def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """
    Extract text from PDF or DOCX file using real parsing libraries.
    Returns the concatenated text content, or empty string on failure.
    """
    try:
        if filename.lower().endswith(".pdf"):
            return _extract_pdf_text(file_content)
        elif filename.lower().endswith(".docx"):
            return _extract_docx_text(file_content)
        else:
            logger.warning(f"Unsupported file format: {filename}")
            return ""
    except Exception as e:
        logger.error(f"Failed to extract text from {filename}: {e}")
        return ""


def _extract_pdf_text(file_content: bytes) -> str:
    """Extract text from PDF bytes using PyPDF2."""
    from PyPDF2 import PdfReader

    reader = PdfReader(io.BytesIO(file_content))
    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    raw = "\n".join(pages_text)
    # Clean excessive whitespace while preserving line breaks
    cleaned = re.sub(r"[ \t]+", " ", raw)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def _extract_docx_text(file_content: bytes) -> str:
    """Extract text from DOCX bytes using python-docx."""
    from docx import Document

    doc = Document(io.BytesIO(file_content))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    raw = "\n".join(paragraphs)
    return raw.strip()


def parse_resume_text(text: str) -> dict:
    """
    Parse text to extract structured data (name, email, phone).
    """
    data = {}

    # Extract Email
    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        data['email'] = email_match.group(0)

    # Extract Phone
    phone_match = re.search(r'(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', text)
    if phone_match:
        data['phone_number'] = phone_match.group(0)

    # Heuristic for Name (first non-empty line if short enough)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if lines:
        first_line = lines[0]
        if len(first_line.split()) <= 4:
            data['name'] = first_line

    return data
