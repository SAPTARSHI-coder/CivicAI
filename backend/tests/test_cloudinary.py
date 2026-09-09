from unittest.mock import patch, MagicMock, PropertyMock, AsyncMock
import pytest
from httpx import ASGITransport, AsyncClient
from app.core.config import Settings, settings
from app.services.cloudinary_service import upload_document
from app.core.state import session_store, document_store
from app.main import create_app

def test_cloudinary_configured_property():
    s = Settings(
        CLOUDINARY_CLOUD_NAME="",
        CLOUDINARY_API_KEY="",
        CLOUDINARY_API_SECRET="",
    )
    assert s.cloudinary_configured is False

    s_partial = Settings(
        CLOUDINARY_CLOUD_NAME="demo_cloud",
        CLOUDINARY_API_KEY="12345",
        CLOUDINARY_API_SECRET="",
    )
    assert s_partial.cloudinary_configured is False

    s_full = Settings(
        CLOUDINARY_CLOUD_NAME="demo_cloud",
        CLOUDINARY_API_KEY="12345",
        CLOUDINARY_API_SECRET="secret_key",
    )
    assert s_full.cloudinary_configured is True


def test_upload_document_skipped_when_unconfigured():
    with patch.object(Settings, "cloudinary_configured", new_callable=PropertyMock, return_value=False):
        result = upload_document(b"sample file content", "test.pdf", "test-session-123")
        assert result is None


def test_upload_document_success():
    mock_upload = MagicMock(return_value={
        "secure_url": "https://res.cloudinary.com/demo/image/upload/v1/civicai/test-session-123/my_doc",
        "public_id": "civicai/test-session-123/my_doc"
    })
    
    with patch.object(Settings, "cloudinary_configured", new_callable=PropertyMock, return_value=True), \
         patch.object(settings, "CLOUDINARY_CLOUD_NAME", "demo"), \
         patch.object(settings, "CLOUDINARY_API_KEY", "key"), \
         patch.object(settings, "CLOUDINARY_API_SECRET", "secret"), \
         patch("cloudinary.config") as mock_config, \
         patch("cloudinary.uploader.upload", mock_upload):
        
        result = upload_document(b"fake file bytes", "My Document (v1).pdf", "sess-456")
        
        assert result is not None
        assert result["url"] == "https://res.cloudinary.com/demo/image/upload/v1/civicai/test-session-123/my_doc"
        assert result["public_id"] == "civicai/test-session-123/my_doc"
        
        mock_upload.assert_called_once()
        _, kwargs = mock_upload.call_args
        assert kwargs["folder"] == "civicai/sess-456"
        assert kwargs["resource_type"] == "auto"
        assert kwargs["public_id"] == "My_Document__v1"


def test_upload_document_exception_handled_gracefully():
    with patch.object(Settings, "cloudinary_configured", new_callable=PropertyMock, return_value=True), \
         patch("cloudinary.config"), \
         patch("cloudinary.uploader.upload", side_effect=RuntimeError("Network timeout")):
        
        result = upload_document(b"fake bytes", "doc.pdf", "sess-789")
        # Must never raise, must return None
        assert result is None


@pytest.mark.asyncio
async def test_analyze_endpoint_returns_document_url_and_session_id():
    app = create_app()
    fake_ai_result = {
        "explanation": "Test explanation",
        "eligibility": {"status": "likely", "text": "Eligible"},
        "checklist": ["Step 1"],
        "missing_documents": []
    }

    mock_provider = MagicMock()
    mock_provider.generate_json = AsyncMock(return_value=fake_ai_result)

    with patch("app.api.v1.endpoints.analyze.parse_document", AsyncMock(return_value="Valid text")), \
         patch("app.api.v1.endpoints.analyze.get_provider", return_value=mock_provider), \
         patch("app.api.v1.endpoints.analyze.upload_document", return_value={
             "url": "https://res.cloudinary.com/demo/image/upload/v1/civicai/sess/sample.pdf",
             "public_id": "civicai/sess/sample"
         }):
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            files = {"file": ("sample.pdf", b"%PDF-1.4 test content", "application/pdf")}
            data = {"language": "English", "provider": "gemini"}
            resp = await ac.post("/api/v1/analyze", files=files, data=data)
            
            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert "session_id" in body
            assert body["document_url"] == "https://res.cloudinary.com/demo/image/upload/v1/civicai/sess/sample.pdf"
            
            # Verify document_store was populated
            sess_id = body["session_id"]
            assert sess_id in document_store
            assert document_store[sess_id]["url"] == "https://res.cloudinary.com/demo/image/upload/v1/civicai/sess/sample.pdf"
            # Verify session_store was populated
            assert sess_id in session_store


@pytest.mark.asyncio
async def test_analyze_endpoint_unconfigured_cloudinary_returns_null_document_url():
    app = create_app()
    fake_ai_result = {
        "explanation": "Test explanation",
        "eligibility": {"status": "likely", "text": "Eligible"},
        "checklist": ["Step 1"],
        "missing_documents": []
    }

    mock_provider = MagicMock()
    mock_provider.generate_json = AsyncMock(return_value=fake_ai_result)

    with patch("app.api.v1.endpoints.analyze.parse_document", AsyncMock(return_value="Valid text")), \
         patch("app.api.v1.endpoints.analyze.get_provider", return_value=mock_provider), \
         patch("app.api.v1.endpoints.analyze.upload_document", return_value=None):
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            files = {"file": ("sample.pdf", b"%PDF-1.4 test content", "application/pdf")}
            data = {"language": "English", "provider": "gemini"}
            resp = await ac.post("/api/v1/analyze", files=files, data=data)
            
            assert resp.status_code == 200, resp.text
            body = resp.json()
            assert "session_id" in body
            assert body["document_url"] is None
            
            sess_id = body["session_id"]
            assert sess_id in document_store
            assert document_store[sess_id] is None
            assert sess_id in session_store
