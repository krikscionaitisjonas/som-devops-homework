from dataclasses import dataclass
from itertools import count
from threading import RLock

from app.models.service_order import ServiceOrder
from app.utils.errors import ConflictError


@dataclass(frozen=True)
class HubListenerRecord:
    id: str
    callback: str
    query: str | None = None


class InMemoryStore:
    """
    In-memory persistence for demo purposes.

    Data is kept only for the process lifetime.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._service_order_sequence = count(1)
        self._hub_sequence = count(1)
        self._service_orders: dict[str, ServiceOrder] = {}
        self._hub_listeners: dict[str, HubListenerRecord] = {}

    def next_service_order_id(self) -> str:
        with self._lock:
            return str(next(self._service_order_sequence))

    def next_hub_id(self) -> str:
        with self._lock:
            return str(next(self._hub_sequence))

    def list_service_orders(self) -> list[ServiceOrder]:
        with self._lock:
            return [order.model_copy(deep=True) for order in self._service_orders.values()]

    def get_service_order(self, service_order_id: str) -> ServiceOrder | None:
        with self._lock:
            order = self._service_orders.get(service_order_id)
            return None if order is None else order.model_copy(deep=True)

    def create_service_order(self, service_order: ServiceOrder) -> ServiceOrder:
        if service_order.id is None:
            raise ValueError("service_order.id must be set before persistence.")

        with self._lock:
            if service_order.id in self._service_orders:
                raise ConflictError(f"ServiceOrder with id '{service_order.id}' already exists.")
            self._service_orders[service_order.id] = service_order.model_copy(deep=True)
            return service_order.model_copy(deep=True)

    def update_service_order(self, service_order: ServiceOrder) -> ServiceOrder:
        if service_order.id is None:
            raise ValueError("service_order.id must be set before persistence.")

        with self._lock:
            if service_order.id not in self._service_orders:
                raise KeyError(service_order.id)
            self._service_orders[service_order.id] = service_order.model_copy(deep=True)
            return service_order.model_copy(deep=True)

    def delete_service_order(self, service_order_id: str) -> bool:
        with self._lock:
            existed = service_order_id in self._service_orders
            if existed:
                del self._service_orders[service_order_id]
            return existed

    def list_hub_listeners(self) -> list[HubListenerRecord]:
        with self._lock:
            return list(self._hub_listeners.values())

    def get_hub_listener(self, listener_id: str) -> HubListenerRecord | None:
        with self._lock:
            return self._hub_listeners.get(listener_id)

    def create_hub_listener(self, callback: str, query: str | None) -> HubListenerRecord:
        with self._lock:
            listener_id = self.next_hub_id()
            listener = HubListenerRecord(id=listener_id, callback=callback, query=query)
            self._hub_listeners[listener_id] = listener
            return listener

    def delete_hub_listener(self, listener_id: str) -> bool:
        with self._lock:
            existed = listener_id in self._hub_listeners
            if existed:
                del self._hub_listeners[listener_id]
            return existed

