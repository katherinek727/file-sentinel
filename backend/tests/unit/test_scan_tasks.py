import pytest
from unittest.mock import patch, AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import StoredFile
from src.tasks.file_tasks import (
    _extract_file_metadata,
    _scan_file_for_threats,
    _send_file_alert,
)
from tests.factories import create_stored_file


async def test_scan_clean_file(session: AsyncSession, tmp_path):
    file = await create_stored_file(
        session,
        original_name="report.pdf",
        mime_type="application/pdf",
        size=1024,
        processing_status="uploaded",
        scan_status=None,
    )

    with patch("src.tasks.file_tasks.async_session_factory") as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("src.tasks.file_tasks.extract_file_metadata") as mock_next:
            await _scan_file_for_threats(file.id)
            mock_next.delay.assert_called_once_with(file.id)

    await session.refresh(file)
    assert file.scan_status == "clean"
    assert file.requires_attention is False


async def test_scan_suspicious_extension(session: AsyncSession):
    file = await create_stored_file(
        session,
        original_name="malware.exe",
        mime_type="application/octet-stream",
        size=512,
        processing_status="uploaded",
        scan_status=None,
    )

    with patch("src.tasks.file_tasks.async_session_factory") as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("src.tasks.file_tasks.extract_file_metadata"):
            await _scan_file_for_threats(file.id)

    await session.refresh(file)
    assert file.scan_status == "suspicious"
    assert file.requires_attention is True
    assert ".exe" in file.scan_details


async def test_scan_oversized_file(session: AsyncSession):
    file = await create_stored_file(
        session,
        original_name="big.zip",
        mime_type="application/zip",
        size=20 * 1024 * 1024,
        processing_status="uploaded",
        scan_status=None,
    )

    with patch("src.tasks.file_tasks.async_session_factory") as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("src.tasks.file_tasks.extract_file_metadata"):
            await _scan_file_for_threats(file.id)

    await session.refresh(file)
    assert file.scan_status == "suspicious"
    assert "10 MB" in file.scan_details


async def test_extract_metadata_text_file(session: AsyncSession, tmp_path):
    content = b"line one\nline two\nline three"
    stored_name = "textfile.txt"
    (tmp_path / stored_name).write_bytes(content)

    file = await create_stored_file(
        session,
        original_name="textfile.txt",
        stored_name=stored_name,
        mime_type="text/plain",
        processing_status="processing",
    )

    with patch("src.tasks.file_tasks.async_session_factory") as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with patch("src.tasks.file_tasks.STORAGE_DIR", tmp_path):
            with patch("src.tasks.file_tasks.send_file_alert"):
                await _extract_file_metadata(file.id)

    await session.refresh(file)
    assert file.processing_status == "processed"
    assert file.metadata_json["line_count"] == 3
    assert file.metadata_json["extension"] == ".txt"


async def test_send_alert_for_clean_file(session: AsyncSession):
    file = await create_stored_file(
        session,
        processing_status="processed",
        requires_attention=False,
    )

    with patch("src.tasks.file_tasks.async_session_factory") as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        await _send_file_alert(file.id)

    result = await session.execute(
        __import__("sqlalchemy").select(
            __import__("src.models.alert", fromlist=["Alert"]).Alert
        ).where(
            __import__("src.models.alert", fromlist=["Alert"]).Alert.file_id == file.id
        )
    )
    alert = result.scalar_one()
    assert alert.level == "info"


async def test_scan_skips_nonexistent_file(session: AsyncSession):
    with patch("src.tasks.file_tasks.async_session_factory") as mock_factory:
        mock_factory.return_value.__aenter__ = AsyncMock(return_value=session)
        mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        # Should not raise
        await _scan_file_for_threats("nonexistent-id")
