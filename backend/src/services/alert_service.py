from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.alert_repository import AlertRepository
from src.schemas.alert import AlertResponse
from src.schemas.pagination import PagedResponse, PaginationParams


class AlertService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = AlertRepository(session)

    async def list_alerts(self, params: PaginationParams) -> PagedResponse[AlertResponse]:
        alerts, total = await self._repo.list(params)
        return PagedResponse.create(
            items=[AlertResponse.model_validate(a) for a in alerts],
            total=total,
            params=params,
        )
