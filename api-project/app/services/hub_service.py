from app.models.hub import Hub, HubCreate
from app.repositories.memory_store import InMemoryStore
from app.services.service_order_service import get_store
from app.utils.errors import NotFoundError


class HubService:
    def __init__(self, store: InMemoryStore, resource_path: str = "/hub") -> None:
        self._store = store
        self._resource_path = resource_path.rstrip("/") or "/hub"

    def register_listener(self, payload: HubCreate) -> Hub:
        listener = self._store.create_hub_listener(
            callback=str(payload.callback),
            query=payload.query,
        )
        return Hub(id=listener.id, callback=listener.callback, query=listener.query)

    def unregister_listener(self, listener_id: str) -> None:
        deleted = self._store.delete_hub_listener(listener_id)
        if not deleted:
            raise NotFoundError(f"Hub listener with id '{listener_id}' was not found.")

    def location_for(self, listener_id: str) -> str:
        return f"{self._resource_path}/{listener_id}"


_hub_service = HubService(store=get_store())


def get_hub_service() -> HubService:
    return _hub_service

