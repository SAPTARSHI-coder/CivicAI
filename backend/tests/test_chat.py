import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient
from app.core.state import session_store

@pytest.mark.asyncio
async def test_chat_session_not_found(client: AsyncClient):
    resp = await client.post("/api/v1/chat", json={
        "session_id": "nonexistent-session-id",
        "message": "Hello"
    })
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_chat_success(client: AsyncClient):
    session_id = "test-active-session"
    session_store[session_id] = [
        {"role": "user", "content": "Analyze doc"},
        {"role": "assistant", "content": "Doc summary"}
    ]

    mock_provider = MagicMock()
    mock_provider.chat = AsyncMock(return_value="Yes, you qualify for this scheme.")

    with patch("app.api.v1.endpoints.chat.get_provider", return_value=mock_provider), \
         patch("app.api.v1.endpoints.chat.log_chat_message") as mock_log_chat:

        resp = await client.post("/api/v1/chat", json={
            "session_id": session_id,
            "message": "Do I qualify?",
            "provider": "gemini"
        })

        assert resp.status_code == 200
        data = resp.json()
        assert data["reply"] == "Yes, you qualify for this scheme."
        assert len(session_store[session_id]) == 4
