from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alert import Alert
from src.schemas.pagination import PaginationParams


class AlertRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self, params: PaginationParams) -> tuple[list[Alert], int]:
        total_result = await self._session.execute(
            select(func.count()).select_from(Alert)
        )
        total = total_result.scalar_one()

        result = await self._session.execute(
            select(Alert)
            .order_by(Alert.created_at.desc())
            .limit(params.page_size)
            .offset(params.offset)
        )
        return list(result.scalars().all()), total

    async def create(self, file_id: str, level: str, message: str) -> Alert:
        alert = Alert(file_id=file_id, level=level, message=message)
        self._session.add(alert)
        await self._session.flush()
        await self._session.refresh(alert)
        return alert
