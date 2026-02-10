import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.health import router as health_router
from app.error_handlers import register_error_handlers
from app.logging_config import configure_logging
from app.settings import get_settings

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting %s (%s)", settings.app_name, settings.environment)
    yield
    logger.info("Shutting down %s", settings.app_name)

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

register_error_handlers(app)
app.include_router(health_router)


@app.get("/", tags=["Meta"], summary="Root endpoint")
def root() -> dict[str, str]:
    return {
        "message": settings.app_name,
        "health": "/health",
        "docs": "/docs",
    }

