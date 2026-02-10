from fastapi import APIRouter, Depends, Response, status

from app.models.hub import Hub, HubCreate
from app.services.hub_service import HubService, get_hub_service

router = APIRouter(tags=["Hub"])


@router.post(
    "/hub",
    response_model=Hub,
    status_code=status.HTTP_201_CREATED,
    summary="Register listener",
)
def register_listener(
    payload: HubCreate,
    response: Response,
    service: HubService = Depends(get_hub_service),
) -> Hub:
    created = service.register_listener(payload=payload)
    response.headers["Location"] = service.location_for(created.id)
    return created


@router.delete(
    "/hub/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unregister listener",
)
def unregister_listener(
    id: str, service: HubService = Depends(get_hub_service)
) -> Response:
    service.unregister_listener(listener_id=id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

