import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.file import FileUpdate
from src.schemas.pagination import PaginationParams
from src.services.file_service import FileService
from tests.factories import create_stored_file


@pytest.fixture
def service(session: AsyncSession) -> FileService:
    return FileService(session)


async def test_get_file_returns_file(session, service):
    file = await create_stored_file(session, title="My Doc")
    result = await service.get_file(file.id)
    assert result.id == file.id
    assert result.title == "My Doc"


async def test_get_file_raises_404_for_missing(service):
    with pytest.raises(HTTPException) as exc_info:
        await service.get_file("nonexistent-id")
    assert exc_info.value.status_code == 404


async def test_list_files_returns_paged_response(session, service):
    for i in range(3):
        await create_stored_file(session, title=f"File {i}")

    params = PaginationParams(page=1, page_size=10)
    result = await service.list_files(params)

    assert result.total >= 3
    assert len(result.items) >= 3
    assert result.page == 1


async def test_list_files_pagination(session, service):
    for i in range(5):
        await create_stored_file(session, title=f"Paginated {i}")

    params = PaginationParams(page=1, page_size=2)
    result = await service.list_files(params)

    assert len(result.items) == 2
    assert result.page_size == 2
    assert result.total_pages >= 1


async def test_update_file_changes_title(session, service):
    file = await create_stored_file(session, title="Old Title")
    result = await service.update_file(file.id, FileUpdate(title="New Title"))
    assert result.title == "New Title"


async def test_update_file_raises_404_for_missing(service):
    with pytest.raises(HTTPException) as exc_info:
        await service.update_file("nonexistent-id", FileUpdate(title="X"))
    assert exc_info.value.status_code == 404


async def test_create_file_stores_and_returns(session, service, tmp_path):
    upload = MagicMock()
    upload.filename = "hello.txt"
    upload.content_type = "text/plain"
    upload.read = AsyncMock(return_value=b"hello world")

    with patch("src.services.file_service.STORAGE_DIR", tmp_path):
        result = await service.create_file(title="Hello", upload=upload)

    assert result.title == "Hello"
    assert result.original_name == "hello.txt"
    assert result.size == len(b"hello world")
    assert result.processing_status == "uploaded"


async def test_create_file_raises_400_for_empty(service):
    upload = MagicMock()
    upload.filename = "empty.txt"
    upload.content_type = "text/plain"
    upload.read = AsyncMock(return_value=b"")

    with pytest.raises(HTTPException) as exc_info:
        await service.create_file(title="Empty", upload=upload)
    assert exc_info.value.status_code == 400


async def test_delete_file_removes_record(session, service, tmp_path):
    file = await create_stored_file(session, stored_name="todelete.txt")
    fake_path = tmp_path / "todelete.txt"
    fake_path.write_bytes(b"data")

    with patch("src.services.file_service.STORAGE_DIR", tmp_path):
        await service.delete_file(file.id)

    with pytest.raises(HTTPException):
        await service.get_file(file.id)

    assert not fake_path.exists()


async def test_delete_file_raises_404_for_missing(service):
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_file("nonexistent-id")
    assert exc_info.value.status_code == 404
