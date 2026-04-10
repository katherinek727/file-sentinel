import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.core.config import get_settings
from src.core.database import STORAGE_DIR
from src.models.alert import Alert
from src.models.file import StoredFile
from src.tasks.celery_app import celery_app


def _make_session() -> tuple[async_sessionmaker[AsyncSession], object]:
    """Create a fresh engine + session factory bound to the current event loop."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    factory = async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
    return factory, engine


async def _scan_file_for_threats(file_id: str) -> None:
    factory, engine = _make_session()
    try:
        async with factory() as session:
            file: StoredFile | None = await session.get(StoredFile, file_id)
            if not file:
                return

            file.processing_status = "processing"
            reasons: list[str] = []
            extension = Path(file.original_name).suffix.lower()

            if extension in {".exe", ".bat", ".cmd", ".sh", ".js"}:
                reasons.append(f"suspicious extension: {extension}")

            if file.size > 10 * 1024 * 1024:
                reasons.append("file exceeds 10 MB limit")

            if (
                extension == ".pdf"
                and file.mime_type not in {"application/pdf", "application/octet-stream"}
            ):
                reasons.append("PDF extension does not match MIME type")

            file.scan_status = "suspicious" if reasons else "clean"
            file.scan_details = ", ".join(reasons) if reasons else "no threats found"
            file.requires_attention = bool(reasons)
            await session.commit()
    finally:
        await engine.dispose()

    extract_file_metadata.delay(file_id)


async def _extract_file_metadata(file_id: str) -> None:
    factory, engine = _make_session()
    try:
        async with factory() as session:
            file: StoredFile | None = await session.get(StoredFile, file_id)
            if not file:
                return

            stored_path = STORAGE_DIR / file.stored_name
            if not stored_path.exists():
                file.processing_status = "failed"
                file.scan_status = file.scan_status or "failed"
                file.scan_details = "stored file not found during metadata extraction"
                await session.commit()
                send_file_alert.delay(file_id)
                return

            metadata: dict = {
                "extension": Path(file.original_name).suffix.lower(),
                "size_bytes": file.size,
                "mime_type": file.mime_type,
            }

            if file.mime_type.startswith("text/"):
                content = stored_path.read_text(encoding="utf-8", errors="ignore")
                metadata["line_count"] = len(content.splitlines())
                metadata["char_count"] = len(content)
            elif file.mime_type == "application/pdf":
                content_bytes = stored_path.read_bytes()
                metadata["approx_page_count"] = max(content_bytes.count(b"/Type /Page"), 1)

            file.metadata_json = metadata
            file.processing_status = "processed"
            await session.commit()
    finally:
        await engine.dispose()

    send_file_alert.delay(file_id)


async def _send_file_alert(file_id: str) -> None:
    factory, engine = _make_session()
    try:
        async with factory() as session:
            file: StoredFile | None = await session.get(StoredFile, file_id)
            if not file:
                return

            if file.processing_status == "failed":
                level, message = "critical", "File processing failed"
            elif file.requires_attention:
                level = "warning"
                message = f"File requires attention: {file.scan_details}"
            else:
                level, message = "info", "File processed successfully"

            session.add(Alert(file_id=file_id, level=level, message=message))
            await session.commit()
    finally:
        await engine.dispose()


@celery_app.task(name="tasks.scan_file_for_threats")
def scan_file_for_threats(file_id: str) -> None:
    asyncio.run(_scan_file_for_threats(file_id))


@celery_app.task(name="tasks.extract_file_metadata")
def extract_file_metadata(file_id: str) -> None:
    asyncio.run(_extract_file_metadata(file_id))


@celery_app.task(name="tasks.send_file_alert")
def send_file_alert(file_id: str) -> None:
    asyncio.run(_send_file_alert(file_id))
