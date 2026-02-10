import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.utils.errors import (
    ConflictError,
    InvalidFieldSelectionError,
    InvalidFilterError,
    NotFoundError,
)

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
    @app.exception_handler(ValidationError)
    async def pydantic_validation_exception_handler(
        request: Request, exc: ValidationError
    ) -> JSONResponse:
        logger.warning("Pydantic validation failed on %s: %s", request.url.path, exc.errors())
        return JSONResponse(
            status_code=400,
            content=_error_payload(
                code="INVALID_REQUEST",
                reason="Payload validation failed",
                message="One or more payload fields are invalid.",
                status=400,
            ),
        )

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

    @app.exception_handler(InvalidFilterError)
    async def invalid_filter_exception_handler(
        request: Request, exc: InvalidFilterError
    ) -> JSONResponse:
        logger.warning("Invalid filter on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=400,
            content=_error_payload(
                code="INVALID_FILTER",
                reason=str(exc),
                message="Filtering query is invalid for this endpoint.",
                status=400,
            ),
        )

    @app.exception_handler(InvalidFieldSelectionError)
    async def invalid_fields_exception_handler(
        request: Request, exc: InvalidFieldSelectionError
    ) -> JSONResponse:
        logger.warning("Invalid fields selection on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=400,
            content=_error_payload(
                code="INVALID_FIELDS",
                reason=str(exc),
                message="Requested fields selection is invalid.",
                status=400,
            ),
        )

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(
        request: Request, exc: NotFoundError
    ) -> JSONResponse:
        logger.warning("Resource not found on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=404,
            content=_error_payload(
                code="NOT_FOUND",
                reason=str(exc),
                message="Requested resource was not found.",
                status=404,
            ),
        )

    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(
        request: Request, exc: ConflictError
    ) -> JSONResponse:
        logger.warning("Conflict on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=409,
            content=_error_payload(
                code="CONFLICT",
                reason=str(exc),
                message="Request conflicts with current resource state.",
                status=409,
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

