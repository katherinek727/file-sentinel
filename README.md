# File Sentinel

> A production-grade fullstack file management platform with async threat scanning, metadata extraction, and real-time alert feeds.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Key Design Decisions](#key-design-decisions)
- [Known Bugs Fixed](#known-bugs-fixed)

---

## Overview

File Sentinel allows users to upload files through a modern web interface. Each uploaded file is asynchronously processed through a multi-stage Celery pipeline:

1. **Threat Scan** — checks for suspicious file extensions, oversized files, and MIME type mismatches
2. **Metadata Extraction** — extracts line counts, character counts, page counts, and MIME info
3. **Alert Generation** — creates a structured alert record (`info`, `warning`, or `critical`) based on scan results

All files and alerts are paginated, searchable, and downloadable from the UI.

---

## Tech Stack

| Layer     | Technology                                      |
|-----------|-------------------------------------------------|
| Backend   | Python 3.14, FastAPI, SQLAlchemy 2 (async)      |
| Worker    | Celery 5, Redis                                 |
| Database  | PostgreSQL 16                                   |
| Migrations| Alembic                                         |
| Frontend  | Next.js 14 (App Router), React 18, TypeScript   |
| Styling   | CSS Modules, CSS Custom Properties              |
| Container | Docker, Docker Compose                          |
| Testing   | pytest, pytest-asyncio, httpx, aiosqlite        |

---

## Architecture

### Backend — Layered Architecture

```
src/
├── api/v1/          # HTTP routers (thin layer, no business logic)
│   ├── files.py     # GET, POST, PATCH, DELETE, download
│   └── alerts.py    # GET with pagination
├── core/
│   ├── config.py    # Typed settings via pydantic-settings (@lru_cache)
│   └── database.py  # Single async engine, session factory, Base, STORAGE_DIR
├── models/
│   ├── file.py      # StoredFile ORM model
│   └── alert.py     # Alert ORM model (CASCADE delete)
├── repositories/
│   ├── file_repository.py   # CRUD + paginated list
│   └── alert_repository.py  # Paginated list + create
├── schemas/
│   ├── file.py        # FileResponse, FileCreate, FileUpdate
│   ├── alert.py       # AlertResponse
│   └── pagination.py  # Generic PagedResponse[T], PaginationParams
├── services/
│   ├── file_service.py   # Business logic, file I/O, HTTP error handling
│   └── alert_service.py  # Alert pagination
├── tasks/
│   ├── celery_app.py  # Celery instance and configuration
│   └── file_tasks.py  # scan → extract → alert pipeline
└── main.py            # FastAPI app, CORS, router registration
```

### Frontend — Layered Architecture

```
src/
├── api/
│   ├── client.ts   # Base fetch wrapper with ApiError class
│   ├── files.ts    # filesApi (list, get, create, update, delete, downloadUrl)
│   └── alerts.ts   # alertsApi (list)
├── types/
│   ├── file.ts        # FileItem, CreateFilePayload
│   ├── alert.ts       # AlertItem
│   └── pagination.ts  # PaginationParams, PagedResponse<T>
├── hooks/
│   ├── useFiles.ts    # State, loading, error, fetch, create, remove
│   └── useAlerts.ts   # State, loading, error, fetch
├── components/
│   ├── FileTable.tsx      # File list with scan status and download
│   ├── AlertTable.tsx     # Alert list with level badges
│   ├── UploadModal.tsx    # Animated upload dialog with dropzone
│   ├── Pagination.tsx     # Page navigation component
│   └── StatusBadge.tsx    # Coloured status indicator
└── app/
    ├── layout.tsx         # Root layout, metadata, global CSS
    ├── page.tsx           # Page composition (hooks + components)
    ├── page.module.css    # Page-level styles
    └── globals.css        # Design tokens (CSS custom properties)
```

### Processing Pipeline

```
POST /api/v1/files
       │
       ▼
  FileService.create_file()
  → writes file to disk
  → inserts StoredFile record (status: "uploaded")
       │
       ▼
  scan_file_for_threats.delay(file_id)   [Celery Task 1]
  → checks extension, size, MIME mismatch
  → sets scan_status: "clean" | "suspicious"
       │
       ▼
  extract_file_metadata.delay(file_id)   [Celery Task 2]
  → extracts line_count, char_count, page_count
  → sets processing_status: "processed" | "failed"
       │
       ▼
  send_file_alert.delay(file_id)         [Celery Task 3]
  → creates Alert record (info / warning / critical)
```

---

## Project Structure

```
.
├── backend/
│   ├── src/                  # Application source
│   ├── migrations/           # Alembic migration files
│   ├── tests/
│   │   ├── unit/             # Service and task unit tests
│   │   ├── integration/      # API endpoint integration tests
│   │   ├── conftest.py       # In-memory SQLite fixtures
│   │   └── factories.py      # Test data factories
│   ├── storage/files/        # Uploaded file storage (gitignored)
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/                  # Application source
│   ├── public/               # Static assets
│   ├── Dockerfile
│   └── package.json
├── docker-compose.dev.yml
├── .env.dev                  # Development environment variables
└── README.md
```

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### 1. Clone the repository

```bash
git clone https://github.com/your-username/file-sentinel.git
cd file-sentinel
```

### 2. Start all services

```bash
docker compose -f docker-compose.dev.yml up --build
```

This starts:
- `backend` — FastAPI on port 8000
- `backend-worker` — Celery worker
- `backend-db` — PostgreSQL on port 5433 (host) → 5432 (container)
- `backend-redis` — Redis on port 6379
- `frontend` — Next.js on port 3000

### 3. Run database migrations

```bash
docker exec -it backend alembic upgrade head
```

### 4. Open the application

| Service       | URL                        |
|---------------|----------------------------|
| Frontend      | http://localhost:3000      |
| API Docs      | http://localhost:8000/docs |
| ReDoc         | http://localhost:8000/redoc|

---

## Environment Variables

Configured in `.env.dev`. Copy to `.env` for production use.

| Variable              | Description                          | Default                          |
|-----------------------|--------------------------------------|----------------------------------|
| `POSTGRES_USER`       | PostgreSQL username                  | `postgres`                       |
| `POSTGRES_PASSWORD`   | PostgreSQL password                  | `postgres`                       |
| `POSTGRES_DB`         | Database name                        | `test`                           |
| `POSTGRES_HOST`       | Database hostname                    | `backend-db`                     |
| `PGPORT`              | PostgreSQL port (internal)           | `5432`                           |
| `CELERY_BROKER_URL`   | Redis connection URL for Celery      | `redis://backend-redis:6379/0`   |
| `NEXT_PUBLIC_API_URL` | Backend base URL for the frontend    | `http://localhost:8000`          |

---

## API Reference

All endpoints are versioned under `/api/v1`.

### Files

| Method   | Endpoint                      | Description                        |
|----------|-------------------------------|------------------------------------|
| `GET`    | `/api/v1/files`               | List files (paginated)             |
| `POST`   | `/api/v1/files`               | Upload a new file (multipart form) |
| `GET`    | `/api/v1/files/{id}`          | Get file details by ID             |
| `PATCH`  | `/api/v1/files/{id}`          | Update file title                  |
| `DELETE` | `/api/v1/files/{id}`          | Delete file and remove from disk   |
| `GET`    | `/api/v1/files/{id}/download` | Download the original file         |

### Alerts

| Method | Endpoint           | Description                  |
|--------|--------------------|------------------------------|
| `GET`  | `/api/v1/alerts`   | List alerts (paginated)      |

### Pagination

All list endpoints accept query parameters:

| Parameter   | Type    | Default | Constraints  |
|-------------|---------|---------|--------------|
| `page`      | integer | `1`     | `>= 1`       |
| `page_size` | integer | `20`    | `1` – `100`  |

Response shape:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

### File Upload

```bash
curl -X POST http://localhost:8000/api/v1/files \
  -F "title=My Document" \
  -F "file=@/path/to/file.pdf"
```

---

## Running Tests

Tests use an in-memory SQLite database — no running services required.

```bash
# Inside the container
docker exec -it backend uv run pytest

# With verbose output
docker exec -it backend uv run pytest -v

# Run only unit tests
docker exec -it backend uv run pytest tests/unit/

# Run only integration tests
docker exec -it backend uv run pytest tests/integration/
```

### Test Coverage

| Area                  | What's tested                                              |
|-----------------------|------------------------------------------------------------|
| `FileService`         | get, list, create, update, delete — including 404/400 cases|
| Celery tasks          | scan logic, metadata extraction, alert creation            |
| `GET /api/v1/files`   | pagination, invalid params (422), empty state              |
| `POST /api/v1/files`  | successful upload, empty file (400), missing title (422)   |
| `PATCH /api/v1/files` | title update, not found (404)                              |
| `DELETE /api/v1/files`| deletion, disk cleanup, not found (404)                    |
| `GET /api/v1/alerts`  | pagination, response shape, invalid params (422)           |

---

## Key Design Decisions

### Backend

- **Single DB engine** — `core/database.py` owns the engine and session factory. The original code had duplicate engines in `service.py` and `tasks.py`.
- **Transactional session dependency** — `get_session()` commits on success and rolls back on exception. Repositories use `flush()` to defer commit ownership.
- **Repository pattern** — data access is fully decoupled from business logic. Repositories never raise `HTTPException`; services do.
- **Generic pagination** — `PagedResponse[T]` is a typed generic used for both files and alerts with zero duplication.
- **Celery task isolation** — each task uses `asyncio.run()` for a fresh event loop per invocation. The original shared `_worker_loop` global was a race condition under concurrent workers.

### Frontend

- **Layered architecture** — `api/` → `hooks/` → `components/` → `page`. Each layer has a single responsibility.
- **Typed API client** — `ApiError` class with HTTP status code. Proper `FormData` handling (no `Content-Type` header override).
- **CSS Modules + custom properties** — zero runtime CSS-in-JS overhead, full design token system, no Bootstrap dependency.
- **Independent pagination state** — files and alerts paginate independently without resetting each other.

---

## Known Bugs Fixed

| Bug | Fix |
|-----|-----|
| Postgres port mapping `5433:5433` — Postgres never received connections | Fixed to `5433:5432` (container listens on 5432) |
| Shared `_worker_loop` in Celery tasks — race condition under concurrency | Replaced with `asyncio.run()` per task |
| Duplicate DB engine created in `tasks.py` | Removed — reuses `async_session_factory` from `core` |
| No `ondelete=CASCADE` on `Alert.file_id` FK — orphaned rows on file delete | Added `ondelete="CASCADE"` to the foreign key |
| `Content-Type: application/json` set on multipart uploads — broke form parsing | Detect `FormData` body and omit `Content-Type` header |
| Hardcoded `http://localhost:8000` in frontend | Replaced with `NEXT_PUBLIC_API_URL` env variable |
| `basePath: '/test'` in Next.js config — app only accessible at `/test` | Removed, app served at root `/` |
| No input validation on file title | Added `min_length=1, max_length=255` on `FileCreate` and `FileUpdate` |
