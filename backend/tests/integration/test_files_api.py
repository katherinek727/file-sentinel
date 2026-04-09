import io
from unittest.mock import patch

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import create_stored_file


async def test_list_files_empty(client: AsyncClient):
    response = await client.get("/api/v1/files")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "total_pages" in data


async def test_list_files_pagination_params(client: AsyncClient, session: AsyncSession):
    for i in range(5):
        await create_stored_file(session, title=f"Integration File {i}")

    response = await client.get("/api/v1/files?page=1&page_size=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2
    assert data["page_size"] == 2
    assert data["total_pages"] >= 1


async def test_list_files_invalid_page(client: AsyncClient):
    response = await client.get("/api/v1/files?page=0")
    assert response.status_code == 422


async def test_list_files_invalid_page_size(client: AsyncClient):
    response = await client.get("/api/v1/files?page_size=200")
    assert response.status_code == 422


async def test_get_file_success(client: AsyncClient, session: AsyncSession):
    file = await create_stored_file(session, title="Get Me")
    response = await client.get(f"/api/v1/files/{file.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == file.id
    assert data["title"] == "Get Me"


async def test_get_file_not_found(client: AsyncClient):
    response = await client.get("/api/v1/files/nonexistent-id")
    assert response.status_code == 404


async def test_create_file_success(client: AsyncClient, tmp_path):
    with patch("src.services.file_service.STORAGE_DIR", tmp_path):
        with patch("src.api.v1.files.scan_file_for_threats") as mock_task:
            response = await client.post(
                "/api/v1/files",
                data={"title": "Uploaded Doc"},
                files={"file": ("doc.txt", io.BytesIO(b"hello content"), "text/plain")},
            )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Uploaded Doc"
    assert data["original_name"] == "doc.txt"
    assert data["processing_status"] == "uploaded"
    mock_task.delay.assert_called_once_with(data["id"])


async def test_create_file_empty_content(client: AsyncClient, tmp_path):
    with patch("src.services.file_service.STORAGE_DIR", tmp_path):
        response = await client.post(
            "/api/v1/files",
            data={"title": "Empty"},
            files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")},
        )
    assert response.status_code == 400


async def test_create_file_missing_title(client: AsyncClient, tmp_path):
    with patch("src.services.file_service.STORAGE_DIR", tmp_path):
        response = await client.post(
            "/api/v1/files",
            data={"title": ""},
            files={"file": ("doc.txt", io.BytesIO(b"data"), "text/plain")},
        )
    assert response.status_code == 422


async def test_update_file_success(client: AsyncClient, session: AsyncSession):
    file = await create_stored_file(session, title="Old Title")
    response = await client.patch(
        f"/api/v1/files/{file.id}",
        json={"title": "New Title"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


async def test_update_file_not_found(client: AsyncClient):
    response = await client.patch(
        "/api/v1/files/nonexistent-id",
        json={"title": "Whatever"},
    )
    assert response.status_code == 404


async def test_delete_file_success(client: AsyncClient, session: AsyncSession, tmp_path):
    stored_name = "deleteme.txt"
    (tmp_path / stored_name).write_bytes(b"bye")
    file = await create_stored_file(session, stored_name=stored_name)

    with patch("src.services.file_service.STORAGE_DIR", tmp_path):
        response = await client.delete(f"/api/v1/files/{file.id}")

    assert response.status_code == 204

    get_response = await client.get(f"/api/v1/files/{file.id}")
    assert get_response.status_code == 404


async def test_delete_file_not_found(client: AsyncClient):
    response = await client.delete("/api/v1/files/nonexistent-id")
    assert response.status_code == 404


async def test_download_file_not_found_on_disk(client: AsyncClient, session: AsyncSession, tmp_path):
    file = await create_stored_file(session, stored_name="missing.txt")
    with patch("src.services.file_service.STORAGE_DIR", tmp_path):
        response = await client.get(f"/api/v1/files/{file.id}/download")
    assert response.status_code == 404
