from collections.abc import Mapping
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from app.models.service_order import ServiceOrder
from app.utils.errors import InvalidFieldSelectionError, InvalidFilterError

_EXACT_FILTER_FIELDS = {"state", "category", "externalId", "priority"}
_DATE_FILTER_FIELDS = {
    "orderDate",
    "completionDate",
    "requestedStartDate",
    "requestedCompletionDate",
    "expectedCompletionDate",
    "startDate",
}
_DATE_OPERATORS = {"gt", "lt", "gte", "lte"}
_SERVICE_ORDER_FIELDS = {field.alias or name for name, field in ServiceOrder.model_fields.items()}


def parse_fields(fields: str | None) -> list[str] | None:
    if fields is None:
        return None

    parsed_fields = [field.strip() for field in fields.split(",") if field.strip()]
    if not parsed_fields:
        raise InvalidFieldSelectionError("Query parameter 'fields' must not be empty.")
    return parsed_fields


def apply_order_filters(
    service_orders: list[ServiceOrder], filters: Mapping[str, str]
) -> list[ServiceOrder]:
    filtered = service_orders
    for filter_key, filter_value in filters.items():
        if filter_key in _EXACT_FILTER_FIELDS:
            filtered = [
                order
                for order in filtered
                if _normalize_scalar(_order_value(order, filter_key)) == filter_value
            ]
            continue

        if "." in filter_key:
            field_name, operator = filter_key.rsplit(".", maxsplit=1)
            if field_name in _DATE_FILTER_FIELDS and operator in _DATE_OPERATORS:
                filtered = _apply_date_filter(filtered, field_name, operator, filter_value)
                continue

        raise InvalidFilterError(f"Unsupported filter '{filter_key}'.")

    return filtered


def project_order(service_order: ServiceOrder, fields: list[str] | None) -> dict[str, Any]:
    data = service_order.model_dump(by_alias=True, mode="json", exclude_none=True)
    if fields is None:
        return data

    invalid_fields = sorted(set(fields).difference(_SERVICE_ORDER_FIELDS))
    if invalid_fields:
        invalid_str = ", ".join(invalid_fields)
        raise InvalidFieldSelectionError(
            f"Unsupported fields in 'fields' selection: {invalid_str}."
        )

    full_data = service_order.model_dump(by_alias=True, mode="json", exclude_none=False)
    return {field: full_data.get(field) for field in fields}


def project_orders(
    service_orders: list[ServiceOrder], fields: list[str] | None
) -> list[dict[str, Any]]:
    return [project_order(service_order=order, fields=fields) for order in service_orders]


def _apply_date_filter(
    service_orders: list[ServiceOrder], field_name: str, operator: str, filter_value: str
) -> list[ServiceOrder]:
    filter_datetime = _parse_datetime(filter_value, field_name=field_name)

    def matches(order: ServiceOrder) -> bool:
        value = _order_value(order, field_name)
        if not isinstance(value, datetime):
            return False

        order_datetime = value if value.tzinfo is not None else value.replace(tzinfo=UTC)
        if operator == "gt":
            return order_datetime > filter_datetime
        if operator == "lt":
            return order_datetime < filter_datetime
        if operator == "gte":
            return order_datetime >= filter_datetime
        return order_datetime <= filter_datetime

    return [order for order in service_orders if matches(order)]


def _order_value(order: ServiceOrder, alias_name: str) -> Any:
    return order.model_dump(by_alias=True, mode="python", exclude_none=False).get(alias_name)


def _normalize_scalar(value: Any) -> str:
    if isinstance(value, Enum):
        return str(value.value)
    if value is None:
        return ""
    return str(value)


def _parse_datetime(value: str, field_name: str) -> datetime:
    raw = value.strip()
    normalized = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:  # pragma: no cover - tiny branch, validated in runtime
        raise InvalidFilterError(
            f"Invalid ISO-8601 datetime value for filter '{field_name}': {value!r}."
        ) from exc
    return parsed if parsed.tzinfo is not None else parsed.replace(tzinfo=UTC)

