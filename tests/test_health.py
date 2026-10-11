from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    """GET /health returns 200 with an ok status."""
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
