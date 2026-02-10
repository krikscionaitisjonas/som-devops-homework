from fastapi.testclient import TestClient


def test_register_hub_listener_returns_201_and_location_header(client: TestClient) -> None:
    response = client.post(
        "/hub",
        json={"callback": "http://listener.example.com/events"},
    )
    assert response.status_code == 201
    assert response.headers["Location"] == "/hub/1"

    body = response.json()
    assert body["id"] == "1"
    assert body["callback"] == "http://listener.example.com/events"
    assert body["query"] is None


def test_register_hub_listener_with_invalid_callback_returns_400(client: TestClient) -> None:
    response = client.post("/hub", json={"callback": "not-a-url"})
    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_REQUEST"


def test_unregister_hub_listener_returns_204(client: TestClient) -> None:
    created = client.post("/hub", json={"callback": "http://listener.example.com/events"})
    listener_id = created.json()["id"]

    deleted = client.delete(f"/hub/{listener_id}")
    assert deleted.status_code == 204


def test_unregister_non_existing_hub_listener_returns_404(client: TestClient) -> None:
    response = client.delete("/hub/777")
    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"

