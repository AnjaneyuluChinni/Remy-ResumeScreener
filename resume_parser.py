import pdfplumber
import docx
import os
from typing import Union


def extract_text_from_pdf(file: Union[str, bytes]) -> str:
    """Extract text from a PDF file."""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(file: Union[str, bytes]) -> str:
    """Extract text from a DOCX file."""
    doc = docx.Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text


def extract_text(file) -> str:
    """Detect file type and extract text accordingly."""
    if hasattr(file, 'name'):
        filename = file.name
    elif isinstance(file, str):
        filename = file
    else:
        raise ValueError("Unsupported file type")
    ext = os.path.splitext(filename)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(file)
    else:
        raise ValueError("Unsupported file format. Please upload a PDF or DOCX file.") 