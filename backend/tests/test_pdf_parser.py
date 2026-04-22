"""
Unit tests for PDF/DOCX text extraction.
Uses synthetic file content — no real files or external services required.
"""

import io
import zipfile

import pytest

from app.services.pdf_parser import extract_text


class TestPdfParser:
    def test_unsupported_content_type_raises(self):
        with pytest.raises(ValueError, match="Unsupported content type"):
            extract_text(b"data", "text/plain")

    def test_docx_extraction(self):
        """Build a minimal valid DOCX in memory and verify text extraction."""
        docx_bytes = _make_minimal_docx("Hello, Contract World!")
        text = extract_text(
            docx_bytes,
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        assert "Hello, Contract World!" in text

    def test_empty_docx_raises(self):
        """A DOCX with no paragraphs should raise ValueError."""
        docx_bytes = _make_minimal_docx("")
        with pytest.raises(ValueError, match="Could not extract any text"):
            extract_text(
                docx_bytes,
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_minimal_docx(text: str) -> bytes:
    """Create a bare-bones DOCX zip with a single paragraph."""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml"
    ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1"
    Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument"
    Target="word/document.xml"/>
</Relationships>"""

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas"
            xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:t>{text}</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>"""

    word_rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>"""

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document_xml)
        zf.writestr("word/_rels/document.xml.rels", word_rels)

    return buf.getvalue()
