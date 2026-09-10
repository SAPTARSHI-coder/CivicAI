import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_list_sample_documents(client: AsyncClient):
    resp = await client.get("/api/v1/samples")
    assert resp.status_code == 200
    samples = resp.json()
    assert isinstance(samples, list)
    assert len(samples) >= 3
    ids = [s["id"] for s in samples]
    assert "pmay" in ids
    assert "nsp" in ids

@pytest.mark.asyncio
async def test_download_sample_document(client: AsyncClient):
    resp = await client.get("/api/v1/samples/nsp/download")
    assert resp.status_code == 200
    assert resp.headers.get("content-type") == "application/pdf"
    assert len(resp.content) > 1000

@pytest.mark.asyncio
async def test_download_sample_not_found(client: AsyncClient):
    resp = await client.get("/api/v1/samples/nonexistent/download")
    assert resp.status_code == 404
