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

## Endpoints

- `GET /` - project metadata
- `GET /health` - service health status
- `GET /docs` - Swagger UI

