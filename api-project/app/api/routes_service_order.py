from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, Response, status

from app.models.service_order import ServiceOrderCreate
from app.services.query_service import parse_fields
from app.services.service_order_service import ServiceOrderService, get_service_order_service

router = APIRouter(tags=["Service Order"])

_SUPPORTED_PATCH_MEDIA_TYPES = {"application/merge-patch+json"}


@router.get("/serviceOrder", summary="List service orders")
def list_service_orders(
    request: Request,
    fields: str | None = Query(
        default=None,
        description="Comma separated list of first-level fields to include in response.",
    ),
    service: ServiceOrderService = Depends(get_service_order_service),
) -> list[dict[str, Any]]:
    selected_fields = parse_fields(fields)
    filters = {key: value for key, value in request.query_params.items() if key != "fields"}
    return service.list_service_orders(filters=filters, fields=selected_fields)


@router.get("/serviceOrder/{id}", summary="Retrieve service order")
def get_service_order(
    id: str,
    fields: str | None = Query(
        default=None,
        description="Comma separated list of first-level fields to include in response.",
    ),
    service: ServiceOrderService = Depends(get_service_order_service),
) -> dict[str, Any]:
    selected_fields = parse_fields(fields)
    return service.get_service_order(service_order_id=id, fields=selected_fields)


@router.post("/serviceOrder", status_code=status.HTTP_201_CREATED, summary="Create service order")
def create_service_order(
    payload: ServiceOrderCreate,
    fields: str | None = Query(
        default=None,
        description="Comma separated list of first-level fields to include in response.",
    ),
    service: ServiceOrderService = Depends(get_service_order_service),
) -> dict[str, Any]:
    selected_fields = parse_fields(fields)
    return service.create_service_order(payload=payload, fields=selected_fields)


@router.patch("/serviceOrder/{id}", summary="Patch service order")
async def patch_service_order(
    id: str,
    request: Request,
    payload: dict[str, Any] = Body(..., description="RFC7386 merge patch payload."),
    service: ServiceOrderService = Depends(get_service_order_service),
) -> dict[str, str]:
    _validate_patch_content_type(request.headers.get("content-type"))
    return service.patch_service_order(service_order_id=id, payload=payload)


@router.delete(
    "/serviceOrder/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete service order",
)
def delete_service_order(
    id: str,
    service: ServiceOrderService = Depends(get_service_order_service),
) -> Response:
    service.delete_service_order(service_order_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _validate_patch_content_type(content_type: str | None) -> None:
    if content_type is None:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="PATCH requires 'Content-Type: application/merge-patch+json'.",
        )

    media_type = content_type.split(";", maxsplit=1)[0].strip().lower()
    if media_type in _SUPPORTED_PATCH_MEDIA_TYPES:
        return

    if media_type == "application/json-patch+json":
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                "application/json-patch+json is optional in TMF641 and not enabled in this demo. "
                "Use application/merge-patch+json."
            ),
        )

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="Unsupported media type for PATCH. Use application/merge-patch+json.",
    )

