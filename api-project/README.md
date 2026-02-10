# TMF641 API Project

Minimal FastAPI skeleton for TMF641 Service Ordering homework.

## Run

```bash
uv run uvicorn app.main:app --reload --port 8080
```

or:

```bash
uv run python main.py
```

## Optional environment variables

- `APP_NAME` (default: `TMF641 Service Ordering Demo`)
- `APP_VERSION` (default: `0.1.0`)
- `APP_DESCRIPTION` (default: project description text)
- `APP_ENV` (`dev`, `test`, `prod`; default: `dev`)
- `APP_HOST` (default: `0.0.0.0`)
- `APP_PORT` (default: `8080`)
- `APP_RELOAD` (`true`/`false`; default: `true`)
- `APP_LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; default: `INFO`)

## Endpoints

- `GET /` - project metadata
- `GET /health` - service health status
- `GET /docs` - Swagger UI

## Included in Phase 1.3

- Base settings from environment variables
- Centralized logging configuration
- Global error handlers for validation, HTTP errors, and unhandled exceptions

