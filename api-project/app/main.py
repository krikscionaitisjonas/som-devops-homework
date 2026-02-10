from fastapi import FastAPI

from app.api.health import router as health_router

app = FastAPI(
    title="TMF641 Service Ordering Demo",
    description="Demo implementation skeleton for TMF641 Service Ordering API.",
    version="0.1.0",
)

app.include_router(health_router)


@app.get("/", tags=["Meta"], summary="Root endpoint")
def root() -> dict[str, str]:
    return {
        "message": "TMF641 Service Ordering Demo API",
        "health": "/health",
        "docs": "/docs",
    }

