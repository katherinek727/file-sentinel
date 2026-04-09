from fastapi import APIRouter

from src.api.v1.alerts import router as alerts_router
from src.api.v1.files import router as files_router

router = APIRouter(prefix="/api/v1")
router.include_router(files_router)
router.include_router(alerts_router)

__all__ = ["router"]
