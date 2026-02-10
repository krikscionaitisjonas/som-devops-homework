import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


class ApiError(BaseModel):
    code: str
    reason: str
    message: str
    status: str


def _error_payload(code: str, reason: str, message: str, status: int) -> dict[str, str]:
    return ApiError(
        code=code,
        reason=reason,
        message=message,
        status=str(status),
    ).model_dump()


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        logger.warning("Validation failed on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=400,
            content=_error_payload(
                code="INVALID_REQUEST",
                reason="Request validation failed",
                message="One or more request fields are invalid.",
                status=400,
            ),
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        detail: Any = exc.detail
        reason = str(detail) if isinstance(detail, str) else "HTTP error"
        logger.warning("HTTP error on %s: %s", request.url.path, reason)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(
                code="HTTP_ERROR",
                reason=reason,
                message="The request could not be completed.",
                status=exc.status_code,
            ),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled error on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content=_error_payload(
                code="INTERNAL_ERROR",
                reason="Internal server error",
                message="An unexpected error occurred.",
                status=500,
            ),
        )

