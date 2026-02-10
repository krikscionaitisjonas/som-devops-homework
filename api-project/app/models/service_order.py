from __future__ import annotations

from datetime import datetime
from typing import Any, Self

from pydantic import Field, ValidationInfo, model_validator

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
    TMFBaseModel,
    TMFEntity,
)
from app.models.enums import (
    ServiceOrderActionType,
    ServiceOrderItemStateType,
    ServiceOrderStateType,
    ServiceStateType,
)

CREATE_SERVER_MANAGED_FIELDS = {
    "id",
    "href",
    "state",
    "orderDate",
    "completionDate",
    "expectedCompletionDate",
    "startDate",
}
PATCH_NON_PATCHABLE_FIELDS = {
    "id",
    "href",
    "externalId",
    "priority",
    "state",
    "orderDate",
    "completionDate",
}
PATCH_NON_PATCHABLE_ORDER_ITEM_FIELDS = {"id", "action", "state"}


def _is_non_empty(value: str | None) -> bool:
    return value is not None and value.strip() != ""


def _has_reference(*values: str | None) -> bool:
    return any(_is_non_empty(value) for value in values)


def _validate_related_party_collection(
    related_parties: list[RelatedParty] | None, scope: str
) -> None:
    for index, related_party in enumerate(related_parties or []):
        if not _is_non_empty(related_party.role):
            raise ValueError(f"{scope}[{index}].role is required.")
        if not _has_reference(related_party.id, related_party.href, related_party.name):
            raise ValueError(
                f"{scope}[{index}] must include at least one of id, href, or name."
            )


def _validate_note_collection(notes: list[Note] | None, scope: str) -> None:
    for index, note in enumerate(notes or []):
        if note.date is None or not _is_non_empty(note.author) or not _is_non_empty(note.text):
            raise ValueError(f"{scope}[{index}] requires date, author, and text.")


def _validate_order_relationship_collection(
    relationships: list[ServiceOrderRelationship] | None, scope: str
) -> None:
    for index, relationship in enumerate(relationships or []):
        if not _is_non_empty(relationship.relationship_type):
            raise ValueError(f"{scope}[{index}].relationshipType is required.")
        if not _has_reference(relationship.id, relationship.href):
            raise ValueError(f"{scope}[{index}] requires id and/or href.")


def _validate_service_restriction(service: ServiceRestriction, scope: str) -> None:
    for index, place in enumerate(service.place or []):
        if not _is_non_empty(place.role):
            raise ValueError(f"{scope}.place[{index}].role is required.")
        if not _has_reference(place.id, place.href):
            raise ValueError(f"{scope}.place[{index}] requires id and/or href.")

    if service.service_specification is not None and not _has_reference(
        service.service_specification.id, service.service_specification.href
    ):
        raise ValueError(f"{scope}.serviceSpecification requires id and/or href.")

    for index, relationship in enumerate(service.service_relationship or []):
        if not _is_non_empty(relationship.relationship_type):
            raise ValueError(f"{scope}.serviceRelationship[{index}].relationshipType is required.")
        if relationship.service is None or not _has_reference(
            relationship.service.id, relationship.service.href
        ):
            raise ValueError(
                f"{scope}.serviceRelationship[{index}].service requires id and/or href."
            )

    for index, characteristic in enumerate(service.service_characteristic or []):
        if (
            not _is_non_empty(characteristic.name)
            or not _is_non_empty(characteristic.value_type)
            or characteristic.value is None
        ):
            raise ValueError(
                f"{scope}.serviceCharacteristic[{index}] requires name, valueType, and value."
            )


class ServiceRestriction(TMFEntity):
    category: str | None = None
    href: str | None = None
    id: str | None = None
    name: str | None = None
    place: list[Place] | None = None
    related_party: list[RelatedParty] | None = Field(default=None, alias="relatedParty")
    service_characteristic: list[Characteristic] | None = Field(
        default=None, alias="serviceCharacteristic"
    )
    service_relationship: list[ServiceRelationship] | None = Field(
        default=None, alias="serviceRelationship"
    )
    service_specification: ServiceSpecificationRef | None = Field(
        default=None, alias="serviceSpecification"
    )
    service_type: str | None = Field(default=None, alias="serviceType")
    state: ServiceStateType | None = None
    supporting_resource: list[ResourceRef] | None = Field(default=None, alias="supportingResource")
    supporting_service: list[ServiceRef] | None = Field(default=None, alias="supportingService")


class ServiceOrderItem(TMFEntity):
    action: ServiceOrderActionType | None = None
    appointment: AppointmentRef | None = None
    id: str | None = None
    order_item_relationship: list[ServiceOrderItemRelationship] | None = Field(
        default=None, alias="orderItemRelationship"
    )
    related_party: list[RelatedParty] | None = Field(default=None, alias="relatedParty")
    service: ServiceRestriction | None = None
    state: ServiceOrderItemStateType | None = None


class ServiceOrder(TMFEntity):
    category: str | None = None
    completion_date: datetime | None = Field(default=None, alias="completionDate")
    description: str | None = None
    expected_completion_date: datetime | None = Field(
        default=None, alias="expectedCompletionDate"
    )
    external_id: str | None = Field(default=None, alias="externalId")
    href: str | None = None
    id: str | None = None
    note: list[Note] | None = None
    notification_contact: str | None = Field(default=None, alias="notificationContact")
    order_date: datetime | None = Field(default=None, alias="orderDate")
    order_item: list[ServiceOrderItem] | None = Field(default=None, alias="orderItem")
    order_relationship: list[ServiceOrderRelationship] | None = Field(
        default=None, alias="orderRelationship"
    )
    priority: str | None = None
    related_party: list[RelatedParty] | None = Field(default=None, alias="relatedParty")
    requested_completion_date: datetime | None = Field(
        default=None, alias="requestedCompletionDate"
    )
    requested_start_date: datetime | None = Field(default=None, alias="requestedStartDate")
    start_date: datetime | None = Field(default=None, alias="startDate")
    state: ServiceOrderStateType | None = None


class ServiceOrderItemCreate(TMFEntity):
    action: ServiceOrderActionType
    appointment: AppointmentRef | None = None
    id: str
    order_item_relationship: list[ServiceOrderItemRelationship] | None = Field(
        default=None, alias="orderItemRelationship"
    )
    related_party: list[RelatedParty] | None = Field(default=None, alias="relatedParty")
    service: ServiceRestriction

    @model_validator(mode="after")
    def validate_create_rules(self) -> Self:
        if self.action != ServiceOrderActionType.ADD and not _has_reference(
            self.service.id, self.service.href
        ):
            raise ValueError(
                "For orderItem.action different from 'add', "
                "service.id and/or service.href is required."
            )

        if self.appointment is not None and not _has_reference(
            self.appointment.id, self.appointment.href
        ):
            raise ValueError("orderItem.appointment requires id and/or href.")

        for index, relationship in enumerate(self.order_item_relationship or []):
            if not _is_non_empty(relationship.relationship_type):
                raise ValueError(
                    f"orderItem.orderItemRelationship[{index}].relationshipType is required."
                )
            if not _is_non_empty(relationship.id):
                raise ValueError(f"orderItem.orderItemRelationship[{index}].id is required.")

        _validate_related_party_collection(self.related_party, "orderItem.relatedParty")
        _validate_service_restriction(self.service, "orderItem.service")
        return self


class ServiceOrderCreate(TMFEntity):
    category: str | None = None
    description: str | None = None
    external_id: str | None = Field(default=None, alias="externalId")
    note: list[Note] | None = None
    notification_contact: str | None = Field(default=None, alias="notificationContact")
    order_item: list[ServiceOrderItemCreate] = Field(alias="orderItem", min_length=1)
    order_relationship: list[ServiceOrderRelationship] | None = Field(
        default=None, alias="orderRelationship"
    )
    priority: str | None = "4"
    related_party: list[RelatedParty] | None = Field(default=None, alias="relatedParty")
    requested_completion_date: datetime | None = Field(
        default=None, alias="requestedCompletionDate"
    )
    requested_start_date: datetime | None = Field(default=None, alias="requestedStartDate")

    @model_validator(mode="before")
    @classmethod
    def validate_server_managed_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        invalid_fields = CREATE_SERVER_MANAGED_FIELDS.intersection(data.keys())
        if invalid_fields:
            field_list = ", ".join(sorted(invalid_fields))
            raise ValueError(f"Create payload cannot include server-managed fields: {field_list}.")

        for index, order_item in enumerate(data.get("orderItem", [])):
            if isinstance(order_item, dict) and "state" in order_item:
                raise ValueError(
                    f"Create payload cannot include orderItem[{index}].state (server-managed)."
                )

        return data

    @model_validator(mode="after")
    def validate_create_collections(self) -> Self:
        _validate_related_party_collection(self.related_party, "relatedParty")
        _validate_note_collection(self.note, "note")
        _validate_order_relationship_collection(self.order_relationship, "orderRelationship")
        return self


class ServiceOrderItemPatch(TMFEntity):
    appointment: AppointmentRef | None = None
    order_item_relationship: list[ServiceOrderItemRelationship] | None = Field(
        default=None, alias="orderItemRelationship"
    )
    related_party: list[RelatedParty] | None = Field(default=None, alias="relatedParty")
    service: ServiceRestriction | None = None

    @model_validator(mode="after")
    def validate_patch_rules(self) -> Self:
        if self.appointment is not None and not _has_reference(
            self.appointment.id, self.appointment.href
        ):
            raise ValueError("orderItem.appointment requires id and/or href.")

        for index, relationship in enumerate(self.order_item_relationship or []):
            if not _is_non_empty(relationship.relationship_type):
                raise ValueError(
                    f"orderItem.orderItemRelationship[{index}].relationshipType is required."
                )
            if not _is_non_empty(relationship.id):
                raise ValueError(f"orderItem.orderItemRelationship[{index}].id is required.")

        _validate_related_party_collection(self.related_party, "orderItem.relatedParty")

        if self.service is not None:
            _validate_service_restriction(self.service, "orderItem.service")

        return self


class ServiceOrderPatch(TMFEntity):
    category: str | None = None
    description: str | None = None
    expected_completion_date: datetime | None = Field(
        default=None, alias="expectedCompletionDate"
    )
    note: list[Note] | None = None
    notification_contact: str | None = Field(default=None, alias="notificationContact")
    order_item: list[ServiceOrderItemPatch] | None = Field(default=None, alias="orderItem")
    order_relationship: list[ServiceOrderRelationship] | None = Field(
        default=None, alias="orderRelationship"
    )
    related_party: list[RelatedParty] | None = Field(default=None, alias="relatedParty")
    requested_completion_date: datetime | None = Field(
        default=None, alias="requestedCompletionDate"
    )
    requested_start_date: datetime | None = Field(default=None, alias="requestedStartDate")
    start_date: datetime | None = Field(default=None, alias="startDate")

    @model_validator(mode="before")
    @classmethod
    def validate_patchable_fields(cls, data: Any) -> Any:
        if not isinstance(data, dict):
            return data

        invalid_fields = PATCH_NON_PATCHABLE_FIELDS.intersection(data.keys())
        if invalid_fields:
            field_list = ", ".join(sorted(invalid_fields))
            raise ValueError(f"Patch payload includes non-patchable fields: {field_list}.")

        raw_order_items = data.get("orderItem", [])
        for index, order_item in enumerate(raw_order_items):
            if not isinstance(order_item, dict):
                continue
            invalid_order_item_fields = PATCH_NON_PATCHABLE_ORDER_ITEM_FIELDS.intersection(
                order_item.keys()
            )
            if invalid_order_item_fields:
                field_list = ", ".join(sorted(invalid_order_item_fields))
                raise ValueError(
                    f"orderItem[{index}] includes non-patchable fields: {field_list}."
                )

        return data

    @model_validator(mode="after")
    def validate_patch_collections(self) -> Self:
        _validate_related_party_collection(self.related_party, "relatedParty")
        _validate_note_collection(self.note, "note")
        _validate_order_relationship_collection(self.order_relationship, "orderRelationship")
        return self

    @model_validator(mode="after")
    def validate_state_based_patch_rules(self, info: ValidationInfo) -> Self:
        if info.context is None:
            return self

        order_state = info.context.get("order_state")
        if order_state is None:
            return self

        state_value = (
            order_state.value
            if isinstance(order_state, ServiceOrderStateType)
            else str(order_state).strip()
        )

        if state_value != ServiceOrderStateType.ACKNOWLEDGED.value:
            conditional_field_provided = any(
                value is not None
                for value in (
                    self.related_party,
                    self.requested_completion_date,
                    self.requested_start_date,
                    self.order_item,
                )
            )
            if conditional_field_provided:
                raise ValueError(
                    "Patch includes fields that are conditionally patchable only in "
                    "'acknowledged' order state."
                )

        return self


class ServiceOrderCreateResponse(TMFBaseModel):
    id: str
    href: str


class ServiceOrderPatchResponse(TMFBaseModel):
    id: str
    href: str

