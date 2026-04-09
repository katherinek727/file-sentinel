from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.models.file import StoredFile


async def create_stored_file(
    session: AsyncSession,
    *,
    title: str = "Test File",
    original_name: str = "test.txt",
    stored_name: str | None = None,
    mime_type: str = "text/plain",
    size: int = 1024,
    processing_status: str = "processed",
    scan_status: str = "clean",
    scan_details: str = "no threats found",
    requires_attention: bool = False,
) -> StoredFile:
    file_id = str(uuid4())
    file = StoredFile(
        id=file_id,
        title=title,
        original_name=original_name,
        stored_name=stored_name or f"{file_id}.txt",
        mime_type=mime_type,
        size=size,
        processing_status=processing_status,
        scan_status=scan_status,
        scan_details=scan_details,
        requires_attention=requires_attention,
    )
    session.add(file)
    await session.commit()
    await session.refresh(file)
    return file


async def create_alert(
    session: AsyncSession,
    *,
    file_id: str,
    level: str = "info",
    message: str = "File processed successfully",
) -> Alert:
    alert = Alert(file_id=file_id, level=level, message=message)
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return alert
