import pytest
from pathlib import Path
from app.services.document_parser import parse_document
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_parse_sample_pdf():
    pdf_path = Path("backend/data/NSP/NSPInstituteFAQV1.7.pdf")
    if not pdf_path.exists():
        pdf_path = Path("data/NSP/NSPInstituteFAQV1.7.pdf")
    assert pdf_path.exists(), "Sample PDF missing"

    content = pdf_path.read_bytes()
    text = await parse_document(content, "NSPInstituteFAQV1.7.pdf")
    assert "NATIONAL SCHOLARSHIP PORTAL" in text.upper() or "INSTITUTE" in text.upper()

@pytest.mark.asyncio
async def test_parse_unsupported_format():
    with pytest.raises(HTTPException) as exc_info:
        await parse_document(b"plain text content", "sample.txt")
    assert exc_info.value.status_code == 400
