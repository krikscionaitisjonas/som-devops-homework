from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime


@router.get("/health", response_model=HealthResponse, summary="Health check")
def get_health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="tmf641-service-ordering-demo",
        version="0.1.0",
        timestamp=datetime.now(timezone.utc),
    )

