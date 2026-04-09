from fastapi import APIRouter, Depends, File, Form, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_session
from src.schemas.file import FileResponse as FileSchema, FileUpdate
from src.schemas.pagination import PagedResponse, PaginationParams
from src.services.file_service import FileService
from src.tasks.file_tasks import scan_file_for_threats

router = APIRouter(prefix="/files", tags=["files"])


def get_file_service(session: AsyncSession = Depends(get_session)) -> FileService:
    return FileService(session)


def get_pagination(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
) -> PaginationParams:
    return PaginationParams(page=page, page_size=page_size)


@router.get("", response_model=PagedResponse[FileSchema])
async def list_files(
    params: PaginationParams = Depends(get_pagination),
    service: FileService = Depends(get_file_service),
) -> PagedResponse[FileSchema]:
    return await service.list_files(params)


@router.post("", response_model=FileSchema, status_code=201)
async def create_file(
    title: str = Form(..., min_length=1, max_length=255),
    file: UploadFile = File(...),
    service: FileService = Depends(get_file_service),
) -> FileSchema:
    stored = await service.create_file(title=title, upload=file)
    scan_file_for_threats.delay(stored.id)
    return FileSchema.model_validate(stored)


@router.get("/{file_id}", response_model=FileSchema)
async def get_file(
    file_id: str,
    service: FileService = Depends(get_file_service),
) -> FileSchema:
    return await service.get_file_response(file_id)


@router.patch("/{file_id}", response_model=FileSchema)
async def update_file(
    file_id: str,
    payload: FileUpdate,
    service: FileService = Depends(get_file_service),
) -> FileSchema:
    return await service.update_file(file_id=file_id, payload=payload)


@router.get("/{file_id}/download", response_class=FileResponse)
async def download_file(
    file_id: str,
    service: FileService = Depends(get_file_service),
) -> FileResponse:
    file, path = await service.get_file_path(file_id)
    return FileResponse(
        path=path,
        media_type=file.mime_type,
        filename=file.original_name,
    )


@router.delete("/{file_id}", status_code=204)
async def delete_file(
    file_id: str,
    service: FileService = Depends(get_file_service),
) -> None:
    await service.delete_file(file_id)
