from collections.abc import Callable, Iterator
from itertools import count
from typing import Any, TypeAlias

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services.service_order_service import get_notification_service, get_store

ServiceOrderPayloadFactory: TypeAlias = Callable[..., dict[str, Any]]


@pytest.fixture(autouse=True)
def reset_in_memory_state() -> Iterator[None]:
    """
    Reset singleton in-memory state between tests.

    The app intentionally uses process-level singletons for demo runtime.
    Tests clear and reset counters to keep cases isolated and deterministic.
    """

    store = get_store()
    notification_service = get_notification_service()

    with store._lock:  # noqa: SLF001 - test-only access to singleton state
        store._service_orders.clear()  # noqa: SLF001
        store._hub_listeners.clear()  # noqa: SLF001
        store._service_order_sequence = count(1)  # noqa: SLF001
        store._hub_sequence = count(1)  # noqa: SLF001

    with notification_service._event_lock:  # noqa: SLF001 - test-only reset
        notification_service._event_id_sequence = count(1)  # noqa: SLF001

    yield


@pytest.fixture
def client() -> Iterator[TestClient]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def service_order_payload_factory() -> ServiceOrderPayloadFactory:
    def _factory(
        *,
        external_id: str = "bss-001",
        category: str = "TMF resource illustration",
        order_item_id: str = "1",
    ) -> dict[str, Any]:
        return {
            "externalId": external_id,
            "category": category,
            "priority": "1",
            "description": "Service order description",
            "orderItem": [
                {
                    "id": order_item_id,
                    "action": "add",
                    "service": {"serviceType": "CFS"},
                }
            ],
        }

    return _factory

