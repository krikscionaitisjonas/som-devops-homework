"""Pydantic models for TMF641 resources."""

from app.models.common import (
    AppointmentRef,
    Characteristic,
    Note,
    Place,
    RelatedParty,
    ResourceRef,
    ServiceOrderItemRelationship,
    ServiceOrderRelationship,
    ServiceRef,
    ServiceRelationship,
    ServiceSpecificationRef,
    TargetServiceSchema,
    TMFEntity,
)
from app.models.enums import (
    ServiceOrderActionType,
    ServiceOrderItemStateType,
    ServiceOrderStateType,
    ServiceStateType,
)
from app.models.hub import Hub, HubCreate, HubRef
from app.models.service_order import (
    ServiceOrder,
    ServiceOrderCreate,
    ServiceOrderCreateResponse,
    ServiceOrderItem,
    ServiceOrderItemCreate,
    ServiceOrderItemPatch,
    ServiceOrderPatch,
    ServiceOrderPatchResponse,
    ServiceRestriction,
)

__all__ = [
    "AppointmentRef",
    "Characteristic",
    "Note",
    "Place",
    "RelatedParty",
    "ResourceRef",
    "Hub",
    "HubCreate",
    "HubRef",
    "ServiceOrderActionType",
    "ServiceOrderCreate",
    "ServiceOrderCreateResponse",
    "ServiceOrderItem",
    "ServiceOrderItemCreate",
    "ServiceOrderItemStateType",
    "ServiceOrderItemRelationship",
    "ServiceOrderItemPatch",
    "ServiceOrderPatch",
    "ServiceOrderPatchResponse",
    "ServiceOrder",
    "ServiceOrderRelationship",
    "ServiceOrderStateType",
    "ServiceRestriction",
    "ServiceRef",
    "ServiceRelationship",
    "ServiceSpecificationRef",
    "ServiceStateType",
    "TMFEntity",
    "TargetServiceSchema",
]

