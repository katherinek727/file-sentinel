from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.alert import AlertResponse
from src.schemas.pagination import PagedResponse, PaginationParams
from src.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])


def get_alert_service(session: AsyncSession = Depends(get_session)) -> AlertService:
    return AlertService(session)


def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


@router.get("", response_model=PagedResponse[AlertResponse])
async def list_alerts(
    params: PaginationParams = Depends(get_pagination),
    service: AlertService = Depends(get_alert_service),
) -> PagedResponse[AlertResponse]:
    return await service.list_alerts(params)
