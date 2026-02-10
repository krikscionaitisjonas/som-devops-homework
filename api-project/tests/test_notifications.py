import json
from collections.abc import Callable
from typing import Any

from fastapi.testclient import TestClient
from pytest import MonkeyPatch

from app.services.service_order_service import get_notification_service


def test_notifications_emitted_for_create_patch_delete(
    client: TestClient,
    monkeypatch: MonkeyPatch,
    service_order_payload_factory: Callable[..., dict[str, Any]],
) -> None:
    captured_payloads: list[dict[str, Any]] = []
    notification_service = get_notification_service()

    def fake_publish(
        callback: str,
        payload: dict[str, Any],
        event_type: str,
        listener_id: str,
    ) -> None:
        assert callback == "http://listener.example.com/events"
        assert listener_id == "1"
        assert payload["eventType"] == event_type
        captured_payloads.append(payload)

    monkeypatch.setattr(notification_service, "_publish_to_listener", fake_publish)

    register = client.post("/hub", json={"callback": "http://listener.example.com/events"})
    assert register.status_code == 201

    created = client.post(
        "/serviceOrder",
        json=service_order_payload_factory(external_id="notif-1"),
    )
    assert created.status_code == 201
    order_id = created.json()["id"]

    patched = client.patch(
        f"/serviceOrder/{order_id}",
        content=json.dumps({"description": "changed"}),
        headers={"Content-Type": "application/merge-patch+json"},
    )
    assert patched.status_code == 200

    deleted = client.delete(f"/serviceOrder/{order_id}")
    assert deleted.status_code == 204

    event_types = [payload["eventType"] for payload in captured_payloads]
    assert event_types == [
        "ServiceOrderCreateNotification",
        "ServiceOrderAttributeValueChangeNotification",
        "ServiceOrderDeleteNotification",
    ]

    for payload in captured_payloads:
        assert payload["eventId"]
        assert payload["eventTime"]
        assert payload["event"]["serviceOrder"]["id"] == order_id


def test_listener_query_filters_notifications_by_event_type(
    client: TestClient,
    monkeypatch: MonkeyPatch,
    service_order_payload_factory: Callable[..., dict[str, Any]],
) -> None:
    captured_event_types: list[str] = []
    notification_service = get_notification_service()

    def fake_publish(
        callback: str,
        payload: dict[str, Any],
        event_type: str,
        listener_id: str,
    ) -> None:
        assert callback == "http://listener.example.com/events"
        assert listener_id == "1"
        captured_event_types.append(str(payload["eventType"]))
        assert event_type == str(payload["eventType"])

    monkeypatch.setattr(notification_service, "_publish_to_listener", fake_publish)

    register = client.post(
        "/hub",
        json={
            "callback": "http://listener.example.com/events",
            "query": "eventType=ServiceOrderDeleteNotification",
        },
    )
    assert register.status_code == 201

    created = client.post(
        "/serviceOrder",
        json=service_order_payload_factory(external_id="notif-2"),
    )
    order_id = created.json()["id"]
    client.patch(
        f"/serviceOrder/{order_id}",
        content=json.dumps({"description": "changed"}),
        headers={"Content-Type": "application/merge-patch+json"},
    )
    client.delete(f"/serviceOrder/{order_id}")

    assert captured_event_types == ["ServiceOrderDeleteNotification"]

