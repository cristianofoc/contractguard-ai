"""
PDF and DOCX text extraction service.

Supports:
- PDF via pdfplumber
- DOCX via python-docx

Returns clean, concatenated text suitable for AI analysis.
"""

import io


def extract_text(file_bytes: bytes, content_type: str) -> str:
    """
    Extract plain text from a PDF or DOCX binary blob.

    Args:
        file_bytes: Raw file content.
        content_type: MIME type string to determine parser.

    Returns:
        Extracted text as a single string.

    Raises:
        ValueError: If the file is unreadable, corrupted, or password-protected.
    """
    if "pdf" in content_type:
        return _extract_from_pdf(file_bytes)
    elif "wordprocessingml" in content_type or "docx" in content_type:
        return _extract_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported content type: {content_type}")


def _extract_from_pdf(file_bytes: bytes) -> str:
    """Use pdfplumber to extract text from a PDF."""
    try:
        import pdfplumber  # lazy import — only required when processing PDFs
    except ImportError as exc:
        raise RuntimeError("pdfplumber is not installed") from exc

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            if not pdf.pages:
                raise ValueError("PDF contains no pages")

            pages_text: list[str] = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text.strip())

            if not pages_text:
                raise ValueError("Could not extract any text from the PDF. It may be scanned.")

            return "\n\n".join(pages_text)
    except pdfplumber.utils.exceptions.PDFSyntaxError as exc:  # type: ignore[attr-defined]
        raise ValueError(f"Corrupted or invalid PDF: {exc}") from exc
    except Exception as exc:
        # Catch password-protected and other edge cases
        if "password" in str(exc).lower() or "encrypted" in str(exc).lower():
            raise ValueError("Password-protected PDFs are not supported") from exc
        raise ValueError(f"Failed to read PDF: {exc}") from exc


def _extract_from_docx(file_bytes: bytes) -> str:
    """Use python-docx to extract text from a DOCX file."""
    try:
        from docx import Document  # lazy import
    except ImportError as exc:
        raise RuntimeError("python-docx is not installed") from exc

    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]

        if not paragraphs:
            raise ValueError("Could not extract any text from the DOCX file.")

        return "\n\n".join(paragraphs)
    except Exception as exc:
        raise ValueError(f"Failed to read DOCX: {exc}") from exc
