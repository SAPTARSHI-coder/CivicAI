import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from app.core.state import session_store, document_store

@pytest.mark.asyncio
async def test_analyze_document_success(client: AsyncClient):
    fake_ai_result = {
        "explanation": "Pradhan Mantri Awas Yojana provides housing aid.",
        "eligibility": {"status": "likely", "text": "Eligible based on income criteria."},
        "checklist": ["Submit income proof", "Apply online"],
        "missing_documents": ["Income certificate"],
    }

    mock_provider = MagicMock()
    mock_provider.generate_json = AsyncMock(return_value=fake_ai_result)

    with patch("app.api.v1.endpoints.analyze.parse_document", AsyncMock(return_value="Extracted text from doc")), \
         patch("app.api.v1.endpoints.analyze.get_provider", return_value=mock_provider), \
         patch("app.api.v1.endpoints.analyze.upload_document", return_value={"url": "https://cloudinary.com/test.pdf", "public_id": "civicai/test"}), \
         patch("app.api.v1.endpoints.analyze.log_analysis_session") as mock_log_session:

        files = {"file": ("pmay.pdf", b"%PDF-1.4 test document content", "application/pdf")}
        data = {"language": "English", "provider": "gemini"}

        resp = await client.post("/api/v1/analyze", files=files, data=data)
        assert resp.status_code == 200
        body = resp.json()

        assert "session_id" in body
        assert body["document_url"] == "https://cloudinary.com/test.pdf"
        assert body["explanation"] == fake_ai_result["explanation"]

        sess_id = body["session_id"]
        assert sess_id in session_store
        assert sess_id in document_store

@pytest.mark.asyncio
async def test_analyze_empty_file_rejected(client: AsyncClient):
    with patch("app.api.v1.endpoints.analyze.parse_document", AsyncMock(return_value="   ")):
        files = {"file": ("empty.pdf", b"%PDF-1.4 blank", "application/pdf")}
        data = {"language": "English", "provider": "gemini"}
        resp = await client.post("/api/v1/analyze", files=files, data=data)
        assert resp.status_code == 400
        assert "readable text" in resp.json().get("error", {}).get("message", "").lower()
