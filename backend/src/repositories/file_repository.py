from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.file import StoredFile
from src.schemas.pagination import PaginationParams


class FileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, file_id: str) -> StoredFile | None:
        return await self._session.get(StoredFile, file_id)

    async def list(self, params: PaginationParams) -> tuple[list[StoredFile], int]:
        total_result = await self._session.execute(
            select(func.count()).select_from(StoredFile)
        )
        total = total_result.scalar_one()

        result = await self._session.execute(
            select(StoredFile)
            .order_by(StoredFile.created_at.desc())
            .limit(params.page_size)
            .offset(params.offset)
        )
        return list(result.scalars().all()), total

    async def create(self, file: StoredFile) -> StoredFile:
        self._session.add(file)
        await self._session.flush()
        await self._session.refresh(file)
        return file

    async def update(self, file: StoredFile) -> StoredFile:
        await self._session.flush()
        await self._session.refresh(file)
        return file

    async def delete(self, file: StoredFile) -> None:
        await self._session.delete(file)
        await self._session.flush()
