from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.v1 import router
from src.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="File Sentinel",
    description="File upload, threat scanning, and alert management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
