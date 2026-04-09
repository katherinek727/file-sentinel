import mimetypes
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import STORAGE_DIR
from src.models.file import StoredFile
from src.repositories.file_repository import FileRepository
from src.schemas.file import FileResponse, FileUpdate
from src.schemas.pagination import PagedResponse, PaginationParams


class FileService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = FileRepository(session)

    async def list_files(self, params: PaginationParams) -> PagedResponse[FileResponse]:
        files, total = await self._repo.list(params)
        return PagedResponse.create(
            items=[FileResponse.model_validate(f) for f in files],
            total=total,
            params=params,
        )

    async def get_file(self, file_id: str) -> StoredFile:
        file = await self._repo.get_by_id(file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found",
            )
        return file

    async def get_file_response(self, file_id: str) -> FileResponse:
        return FileResponse.model_validate(await self.get_file(file_id))

    async def create_file(self, title: str, upload: UploadFile) -> StoredFile:
        content = await upload.read()
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        file_id = str(uuid4())
        suffix = Path(upload.filename or "").suffix
        stored_name = f"{file_id}{suffix}"
        stored_path = STORAGE_DIR / stored_name
        stored_path.write_bytes(content)

        mime = (
            upload.content_type
            or mimetypes.guess_type(stored_name)[0]
            or "application/octet-stream"
        )

        file = StoredFile(
            id=file_id,
            title=title,
            original_name=upload.filename or stored_name,
            stored_name=stored_name,
            mime_type=mime,
            size=len(content),
            processing_status="uploaded",
        )
        return await self._repo.create(file)

    async def update_file(self, file_id: str, payload: FileUpdate) -> FileResponse:
        file = await self.get_file(file_id)
        file.title = payload.title
        updated = await self._repo.update(file)
        return FileResponse.model_validate(updated)

    async def delete_file(self, file_id: str) -> None:
        file = await self.get_file(file_id)
        stored_path = STORAGE_DIR / file.stored_name
        if stored_path.exists():
            stored_path.unlink()
        await self._repo.delete(file)

    async def get_file_path(self, file_id: str) -> tuple[StoredFile, Path]:
        file = await self.get_file(file_id)
        stored_path = STORAGE_DIR / file.stored_name
        if not stored_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Stored file not found on disk",
            )
        return file, stored_path
