import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_field_help_endpoint() -> None:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/metadata/fields")
    assert response.status_code == 200
    data = response.json()
    assert "target_models" in data
    assert "providers" in data
    assert "integrations" in data
