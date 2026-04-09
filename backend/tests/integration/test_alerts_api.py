import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_alert, create_stored_file


async def test_list_alerts_empty(client: AsyncClient):
    response = await client.get("/api/v1/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "total_pages" in data


async def test_list_alerts_returns_data(client: AsyncClient, session: AsyncSession):
    file = await create_stored_file(session)
    await create_alert(session, file_id=file.id, level="warning", message="Suspicious file")

    response = await client.get("/api/v1/alerts")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1

    levels = [item["level"] for item in data["items"]]
    assert "warning" in levels


async def test_list_alerts_pagination(client: AsyncClient, session: AsyncSession):
    file = await create_stored_file(session)
    for i in range(5):
        await create_alert(session, file_id=file.id, message=f"Alert {i}")

    response = await client.get("/api/v1/alerts?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page_size"] == 2


async def test_list_alerts_invalid_page(client: AsyncClient):
    response = await client.get("/api/v1/alerts?page=-1")
    assert response.status_code == 422


async def test_list_alerts_invalid_page_size(client: AsyncClient):
    response = await client.get("/api/v1/alerts?page_size=0")
    assert response.status_code == 422


async def test_alert_fields_shape(client: AsyncClient, session: AsyncSession):
    file = await create_stored_file(session)
    await create_alert(session, file_id=file.id, level="critical", message="Processing failed")

    response = await client.get("/api/v1/alerts")
    assert response.status_code == 200
    item = response.json()["items"][0]

    assert "id" in item
    assert "file_id" in item
    assert "level" in item
    assert "message" in item
    assert "created_at" in item
