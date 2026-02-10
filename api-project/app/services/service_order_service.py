from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from app.models.enums import ServiceOrderItemStateType, ServiceOrderStateType
from app.models.service_order import ServiceOrder, ServiceOrderCreate, ServiceOrderPatch
from app.repositories.memory_store import InMemoryStore
from app.services.query_service import apply_order_filters, project_order, project_orders
from app.utils.errors import NotFoundError


class ServiceOrderService:
    def __init__(self, store: InMemoryStore, resource_path: str = "/serviceOrder") -> None:
        self._store = store
        self._resource_path = resource_path.rstrip("/") or "/serviceOrder"

    def create_service_order(
        self, payload: ServiceOrderCreate, fields: list[str] | None = None
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        service_order_id = self._store.next_service_order_id()
        payload_data = payload.model_dump(by_alias=True, mode="python", exclude_none=True)

        payload_data["id"] = service_order_id
        payload_data["href"] = f"{self._resource_path}/{service_order_id}"
        payload_data["state"] = ServiceOrderStateType.ACKNOWLEDGED.value
        payload_data["orderDate"] = now
        payload_data["completionDate"] = None
        payload_data["startDate"] = None
        payload_data.setdefault("priority", "4")
        payload_data.setdefault(
            "expectedCompletionDate", payload_data.get("requestedCompletionDate")
        )
        payload_data.setdefault("@type", "ServiceOrder")

        for order_item in payload_data.get("orderItem", []):
            if isinstance(order_item, dict):
                order_item["state"] = ServiceOrderItemStateType.ACKNOWLEDGED.value

        created_order = ServiceOrder.model_validate(payload_data)
        persisted_order = self._store.create_service_order(created_order)
        return project_order(persisted_order, fields)

    def list_service_orders(
        self, filters: Mapping[str, str], fields: list[str] | None = None
    ) -> list[dict[str, Any]]:
        service_orders = self._store.list_service_orders()
        filtered_orders = apply_order_filters(service_orders, filters)
        return project_orders(filtered_orders, fields)

    def get_service_order(
        self, service_order_id: str, fields: list[str] | None = None
    ) -> dict[str, Any]:
        service_order = self._store.get_service_order(service_order_id)
        if service_order is None:
            raise NotFoundError(f"ServiceOrder with id '{service_order_id}' was not found.")
        return project_order(service_order, fields)

    def patch_service_order(
        self, service_order_id: str, payload: Mapping[str, Any]
    ) -> dict[str, str]:
        service_order = self._store.get_service_order(service_order_id)
        if service_order is None:
            raise NotFoundError(f"ServiceOrder with id '{service_order_id}' was not found.")

        patch_model = ServiceOrderPatch.model_validate(
            payload, context={"order_state": service_order.state}
        )
        patch_data = patch_model.model_dump(by_alias=True, mode="python", exclude_unset=True)

        if patch_data:
            current_data = service_order.model_dump(
                by_alias=True, mode="python", exclude_none=False
            )
            merged_data = _merge_patch(current_data, patch_data)
            merged_data["id"] = service_order.id
            merged_data["href"] = service_order.href

            updated_order = ServiceOrder.model_validate(merged_data)
            service_order = self._store.update_service_order(updated_order)

        return {
            "id": _required_value(service_order.id, "id"),
            "href": _required_value(service_order.href, "href"),
        }

    def delete_service_order(self, service_order_id: str) -> None:
        deleted = self._store.delete_service_order(service_order_id)
        if not deleted:
            raise NotFoundError(f"ServiceOrder with id '{service_order_id}' was not found.")


def _required_value(value: str | None, field_name: str) -> str:
    if value is None:
        raise ValueError(f"Persisted ServiceOrder is missing required '{field_name}'.")
    return value


def _merge_patch(target: Any, patch: Any) -> Any:
    """
    RFC7386 merge patch for dict-like payloads.

    - Objects are merged recursively
    - Arrays and scalars replace the target value
    - null removes an object member
    """

    if not isinstance(patch, dict):
        return deepcopy(patch)

    if not isinstance(target, dict):
        target = {}

    result: dict[str, Any] = deepcopy(target)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
            continue

        if isinstance(value, dict):
            current_value = result.get(key)
            if isinstance(current_value, dict):
                result[key] = _merge_patch(current_value, value)
            else:
                result[key] = _merge_patch({}, value)
            continue

        result[key] = deepcopy(value)

    return result


_store = InMemoryStore()
_service_order_service = ServiceOrderService(store=_store)


def get_store() -> InMemoryStore:
    return _store


def get_service_order_service() -> ServiceOrderService:
    return _service_order_service

