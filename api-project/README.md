# TMF641 Service Ordering Demo API

FastAPI demo implementation of TMF641 Service Ordering Management API (REST), intended for local demonstration and tooling exercises.

## Quick start

1. Install dependencies:

```bash
uv sync
```

2. Run API server:

```bash
uv run uvicorn app.main:app --reload --port 8080
```

Alternative launcher:

```bash
uv run python main.py
```

3. Open docs:
- Swagger UI: `http://127.0.0.1:8080/docs`
- Health: `http://127.0.0.1:8080/health`

## Environment variables

- `APP_NAME` (default: `TMF641 Service Ordering Demo`)
- `APP_VERSION` (default: `0.1.0`)
- `APP_DESCRIPTION` (default: project description text)
- `APP_ENV` (`dev`, `test`, `prod`; default: `dev`)
- `APP_HOST` (default: `0.0.0.0`)
- `APP_PORT` (default: `8080`)
- `APP_RELOAD` (`true`/`false`; default: `true`)
- `APP_LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; default: `INFO`)

## Implemented endpoints

### ServiceOrder operations

- `GET /serviceOrder`
- `GET /serviceOrder/{id}`
- `POST /serviceOrder`
- `PATCH /serviceOrder/{id}`
- `DELETE /serviceOrder/{id}`

### Notification subscription operations

- `POST /hub`
- `DELETE /hub/{id}`

### Utility endpoints

- `GET /`
- `GET /health`

## Run with Postman

Artifacts:

- Collection: `postman/TMF641_Demo.postman_collection.json`
- Environment (optional): `postman/TMF641_Demo.postman_environment.json`

Run flow:

1. Start server (`uvicorn` command above).
2. Import collection JSON into Postman.
3. Optionally import/select environment JSON.
4. Run collection `TMF641 Service Ordering Demo`.

Notes:

- The collection is runnable even without selecting an environment (collection variables are included).
- If environment is selected, it can override values like `baseUrl` and callback URL.

## What the Postman suite demonstrates

- service order create/list/filter/retrieve/patch/delete flow
- hub register/unregister flow
- negative cases (`400`, `404`, non-patchable fields)
- notification emission attempts on create/patch/delete

## TMF641 coverage assessment

Implemented in this demo:

- Service order operations: `GET/POST/PATCH/DELETE /serviceOrder` and `GET /serviceOrder/{id}`.
- Listener management: `POST /hub`, `DELETE /hub/{id}`.
- Notification payload shape: TMF-style `eventId`, `eventTime`, `eventType`, `event.serviceOrder`.
- Notification delivery: outbound POST to registered callback URL (best-effort).

Not implemented as inbound route:

- `/client/listener` is not exposed by this API because in TMF examples it is the consumer callback endpoint, not the provider management endpoint.

## Known limitations

- In-memory storage only (no persistence)
- Partial TMF641 conformance (not all optional attributes/rules)
- `PATCH` supports merge-patch only (json-patch not enabled)
- Notification delivery is best-effort (no retries/queue)
- No auth

## Quality checks

```bash
uv run ruff check .
uv run mypy .
uv run pytest
```

