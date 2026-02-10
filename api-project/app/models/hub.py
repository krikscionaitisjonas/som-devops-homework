from pydantic import AnyHttpUrl, Field

from app.models.common import TMFBaseModel


class HubCreate(TMFBaseModel):
    callback: AnyHttpUrl
    query: str | None = None


class Hub(TMFBaseModel):
    id: str
    callback: str
    query: str | None = None


class HubRef(TMFBaseModel):
    id: str = Field(description="Identifier of registered hub listener.")
    callback: str
    query: str | None = None

