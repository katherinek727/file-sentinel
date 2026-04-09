# File Sentinel

A fullstack file management platform with async threat scanning and alert feeds.

Built with **FastAPI** · **Next.js** · **PostgreSQL** · **Celery** · **Redis**

---

## Architecture

```
backend/src/
├── api/v1/          # Versioned routers (files, alerts)
├── core/            # Config (pydantic-settings), DB engine, session dependency
├── models/          # SQLAlchemy ORM models
├── repositories/    # Data access layer (pagination, CRUD)
├── schemas/         # Pydantic request/response schemas + PagedResponse[T]
├── services/        # Business logic, file I/O, HTTP error handling
├── tasks/           # Celery app + async scan/metadata/alert tasks
└── main.py          # FastAPI entrypoint

frontend/src/
├── api/             # Typed fetch client (ApiError, filesApi, alertsApi)
├── types/           # Shared TypeScript interfaces
├── hooks/           # useFiles, useAlerts (state + pagination)
├── components/      # FileTable, AlertTable, UploadModal, Pagination, StatusBadge
└── app/             # Next.js layout, page composition, design tokens
```

---

## Getting Started

### 1. Start all services

```bash
docker compose -f docker-compose.dev.yml up --build
```

### 2. Run database migrations

```bash
docker exec -it backend alembic upgrade head
```

### 3. Open the app

| Service  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000        |
| API docs | http://localhost:8000/docs   |

---

## API

All endpoints are versioned under `/api/v1`.

### Files

| Method   | Path                        | Description              |
|----------|-----------------------------|--------------------------|
| `GET`    | `/api/v1/files`             | List files (paginated)   |
| `POST`   | `/api/v1/files`             | Upload a file            |
| `GET`    | `/api/v1/files/{id}`        | Get file by ID           |
| `PATCH`  | `/api/v1/files/{id}`        | Update file title        |
| `DELETE` | `/api/v1/files/{id}`        | Delete file              |
| `GET`    | `/api/v1/files/{id}/download` | Download file          |

### Alerts

| Method | Path               | Description              |
|--------|--------------------|--------------------------|
| `GET`  | `/api/v1/alerts`   | List alerts (paginated)  |

### Pagination

All list endpoints accept `?page=1&page_size=20` and return:

```json
{
  "items": [...],
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3
}
```

---

## Running Tests

```bash
docker exec -it backend uv run pytest
```

Or locally with dev dependencies installed:

```bash
cd backend
uv sync --extra dev
uv run pytest
```

---

## Environment Variables

Copy `.env.dev` and adjust as needed. Key variables:

| Variable             | Description                    | Default                        |
|----------------------|--------------------------------|--------------------------------|
| `POSTGRES_USER`      | PostgreSQL username             | `postgres`                     |
| `POSTGRES_PASSWORD`  | PostgreSQL password             | `postgres`                     |
| `POSTGRES_DB`        | Database name                   | `test`                         |
| `POSTGRES_HOST`      | Database host                   | `backend-db`                   |
| `PGPORT`             | PostgreSQL port                 | `5432`                         |
| `CELERY_BROKER_URL`  | Redis URL for Celery            | `redis://backend-redis:6379/0` |
| `NEXT_PUBLIC_API_URL`| Backend URL for frontend        | `http://localhost:8000`        |
