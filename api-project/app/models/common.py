from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TMFBaseModel(BaseModel):
    """
    Base model for TMF resources.

    - populate_by_name allows using pythonic field names in code.
    - extra=allow keeps compatibility with TMF extension/polymorphism attributes.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class TMFEntity(TMFBaseModel):
    base_type: str | None = Field(default=None, alias="@baseType")
    schema_location: str | None = Field(default=None, alias="@schemaLocation")
    type_: str | None = Field(default=None, alias="@type")


class TMFRef(TMFBaseModel):
    referred_type: str | None = Field(default=None, alias="@referredType")
    href: str | None = None
    id: str | None = None


class Characteristic(TMFBaseModel):
    name: str | None = None
    value: Any | None = None
    value_type: str | None = Field(default=None, alias="valueType")


class Note(TMFBaseModel):
    author: str | None = None
    date: datetime | None = None
    system: str | None = None
    text: str | None = None


class Place(TMFBaseModel):
    href: str | None = None
    id: str | None = None
    name: str | None = None
    role: str | None = None


class RelatedParty(TMFEntity):
    referred_type: str | None = Field(default=None, alias="@referredType")
    href: str | None = None
    id: str | None = None
    name: str | None = None
    role: str | None = None


class AppointmentRef(TMFRef):
    description: str | None = None


class ResourceRef(TMFRef):
    name: str | None = None


class ServiceRef(TMFRef):
    pass


class TargetServiceSchema(TMFBaseModel):
    schema_location: str | None = Field(default=None, alias="@schemaLocation")
    type_: str | None = Field(default=None, alias="@type")


class ServiceSpecificationRef(TMFRef):
    name: str | None = None
    target_service_schema: TargetServiceSchema | None = Field(
        default=None, alias="targetServiceSchema"
    )
    version: str | None = None


class ServiceRelationship(TMFBaseModel):
    relationship_type: str | None = Field(default=None, alias="relationshipType")
    service: ServiceRef | None = None


class ServiceOrderItemRelationship(TMFBaseModel):
    id: str | None = None
    relationship_type: str | None = Field(default=None, alias="relationshipType")


class ServiceOrderRelationship(TMFRef):
    relationship_type: str | None = Field(default=None, alias="relationshipType")

