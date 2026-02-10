import json
from collections.abc import Callable

from fastapi.testclient import TestClient


def test_create_service_order_returns_201_with_server_managed_fields(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    response = client.post("/serviceOrder", json=service_order_payload_factory())
    assert response.status_code == 201

    body = response.json()
    assert body["id"] == "1"
    assert body["href"] == "/serviceOrder/1"
    assert body["state"] == "acknowledged"
    assert body["orderDate"] is not None
    assert body["orderItem"][0]["state"] == "acknowledged"


def test_create_service_order_rejects_server_managed_input(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    payload = service_order_payload_factory()
    payload["state"] = "completed"
    payload["id"] = "client-id"

    response = client.post("/serviceOrder", json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_REQUEST"


def test_create_service_order_requires_order_item(client: TestClient) -> None:
    payload = {
        "externalId": "bss-002",
        "category": "TMF resource illustration",
        "description": "Missing order item",
    }
    response = client.post("/serviceOrder", json=payload)
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_REQUEST"


def test_list_and_get_service_orders(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    create_a = client.post(
        "/serviceOrder", json=service_order_payload_factory(external_id="bss-a", category="A")
    )
    create_b = client.post(
        "/serviceOrder", json=service_order_payload_factory(external_id="bss-b", category="B")
    )
    assert create_a.status_code == 201
    assert create_b.status_code == 201

    listed = client.get("/serviceOrder")
    assert listed.status_code == 200
    assert len(listed.json()) == 2

    order_id = create_a.json()["id"]
    fetched = client.get(f"/serviceOrder/{order_id}")
    assert fetched.status_code == 200
    assert fetched.json()["externalId"] == "bss-a"


def test_list_filters_by_exact_fields(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    client.post("/serviceOrder", json=service_order_payload_factory(external_id="x1", category="A"))
    client.post("/serviceOrder", json=service_order_payload_factory(external_id="x2", category="B"))

    filtered = client.get("/serviceOrder?category=A&state=acknowledged")
    assert filtered.status_code == 200
    body = filtered.json()
    assert len(body) == 1
    assert body[0]["category"] == "A"
    assert body[0]["state"] == "acknowledged"


def test_list_filters_by_datetime_comparison(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    client.post("/serviceOrder", json=service_order_payload_factory(external_id="x1"))
    client.post("/serviceOrder", json=service_order_payload_factory(external_id="x2"))

    filtered = client.get("/serviceOrder?orderDate.gt=2000-01-01T00:00:00Z")
    assert filtered.status_code == 200
    assert len(filtered.json()) == 2


def test_list_rejects_unsupported_filter(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    client.post("/serviceOrder", json=service_order_payload_factory())

    response = client.get("/serviceOrder?unknownFilter=abc")
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_FILTER"


def test_get_service_order_with_fields_projection(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    created = client.post("/serviceOrder", json=service_order_payload_factory())
    order_id = created.json()["id"]

    projected = client.get(f"/serviceOrder/{order_id}?fields=id,href")
    assert projected.status_code == 200
    assert set(projected.json().keys()) == {"id", "href"}


def test_get_service_order_rejects_invalid_field_selection(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    created = client.post("/serviceOrder", json=service_order_payload_factory())
    order_id = created.json()["id"]

    response = client.get(f"/serviceOrder/{order_id}?fields=id,invalidField")
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_FIELDS"


def test_patch_service_order_with_merge_patch(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    created = client.post("/serviceOrder", json=service_order_payload_factory())
    order_id = created.json()["id"]

    patch_response = client.patch(
        f"/serviceOrder/{order_id}",
        content=json.dumps({"description": "Updated description"}),
        headers={"Content-Type": "application/merge-patch+json"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["id"] == order_id

    fetched = client.get(f"/serviceOrder/{order_id}")
    assert fetched.status_code == 200
    assert fetched.json()["description"] == "Updated description"


def test_patch_rejects_non_patchable_fields(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    created = client.post("/serviceOrder", json=service_order_payload_factory())
    order_id = created.json()["id"]

    response = client.patch(
        f"/serviceOrder/{order_id}",
        content=json.dumps({"priority": "2"}),
        headers={"Content-Type": "application/merge-patch+json"},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_REQUEST"


def test_patch_rejects_unsupported_media_type(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    created = client.post("/serviceOrder", json=service_order_payload_factory())
    order_id = created.json()["id"]

    response = client.patch(
        f"/serviceOrder/{order_id}",
        content=json.dumps({"description": "x"}),
        headers={"Content-Type": "application/json-patch+json"},
    )
    assert response.status_code == 415
    assert response.json()["code"] == "HTTP_ERROR"


def test_delete_service_order_and_not_found_afterwards(
    client: TestClient,
    service_order_payload_factory: Callable[..., dict[str, object]],
) -> None:
    created = client.post("/serviceOrder", json=service_order_payload_factory())
    order_id = created.json()["id"]

    deleted = client.delete(f"/serviceOrder/{order_id}")
    assert deleted.status_code == 204

    missing = client.get(f"/serviceOrder/{order_id}")
    assert missing.status_code == 404
    assert missing.json()["code"] == "NOT_FOUND"


def test_delete_non_existing_service_order_returns_404(client: TestClient) -> None:
    response = client.delete("/serviceOrder/404")
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"

