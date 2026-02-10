import json
import logging
from datetime import UTC, datetime
from itertools import count
from threading import RLock
from urllib import parse, request
from urllib.error import HTTPError, URLError

from app.models.notifications import (
    ServiceOrderAttributeValueChangeNotification,
    ServiceOrderCreateNotification,
    ServiceOrderDeleteNotification,
    ServiceOrderEvent,
    ServiceOrderNotification,
    ServiceOrderStateChangeNotification,
)
from app.models.service_order import ServiceOrder
from app.repositories.memory_store import HubListenerRecord, InMemoryStore

logger = logging.getLogger(__name__)


class NotificationService:
    """
    TMF641 notification emitter.

    Notifications are emitted in best-effort mode:
    - if listener delivery fails, API operations continue
    - failures are logged for demo visibility
    """

    def __init__(self, store: InMemoryStore, delivery_timeout_seconds: float = 3.0) -> None:
        self._store = store
        self._delivery_timeout_seconds = delivery_timeout_seconds
        self._event_id_sequence = count(1)
        self._event_lock = RLock()

    def emit_service_order_create(self, service_order: ServiceOrder) -> None:
        notification = ServiceOrderCreateNotification(
            eventId=self._next_event_id(),
            eventTime=datetime.now(UTC),
            event=ServiceOrderEvent(serviceOrder=service_order.model_copy(deep=True)),
        )
        self._emit(notification)

    def emit_service_order_attribute_value_change(self, service_order: ServiceOrder) -> None:
        notification = ServiceOrderAttributeValueChangeNotification(
            eventId=self._next_event_id(),
            eventTime=datetime.now(UTC),
            event=ServiceOrderEvent(serviceOrder=service_order.model_copy(deep=True)),
        )
        self._emit(notification)

    def emit_service_order_state_change(self, service_order: ServiceOrder) -> None:
        notification = ServiceOrderStateChangeNotification(
            eventId=self._next_event_id(),
            eventTime=datetime.now(UTC),
            event=ServiceOrderEvent(serviceOrder=service_order.model_copy(deep=True)),
        )
        self._emit(notification)

    def emit_service_order_delete(self, service_order: ServiceOrder) -> None:
        notification = ServiceOrderDeleteNotification(
            eventId=self._next_event_id(),
            eventTime=datetime.now(UTC),
            event=ServiceOrderEvent(serviceOrder=service_order.model_copy(deep=True)),
        )
        self._emit(notification)

    def _next_event_id(self) -> str:
        with self._event_lock:
            return str(next(self._event_id_sequence)).zfill(5)

    def _emit(self, notification: ServiceOrderNotification) -> None:
        payload = notification.model_dump(by_alias=True, mode="json", exclude_none=True)
        event_type = payload["eventType"]

        logger.info(
            "TMF641 notification emitted type=%s eventId=%s",
            event_type,
            payload["eventId"],
        )

        listeners = self._store.list_hub_listeners()
        for listener in listeners:
            if not _listener_accepts_event(listener, event_type):
                continue
            self._publish_to_listener(listener.callback, payload, event_type, listener.id)

    def _publish_to_listener(
        self, callback: str, payload: dict[str, object], event_type: str, listener_id: str
    ) -> None:
        body = json.dumps(payload).encode("utf-8")
        http_request = request.Request(
            url=callback,
            data=body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=self._delivery_timeout_seconds) as response:
                status = int(response.getcode())
            if status not in {200, 201, 202, 204}:
                logger.warning(
                    "Listener '%s' responded with status=%s for eventType=%s",
                    listener_id,
                    status,
                    event_type,
                )
        except HTTPError as exc:
            logger.warning(
                "Failed to publish notification to listener '%s' (%s): status=%s",
                listener_id,
                callback,
                exc.code,
            )
        except URLError as exc:
            logger.warning(
                "Failed to publish notification to listener '%s' (%s): %s",
                listener_id,
                callback,
                exc.reason,
            )
        except TimeoutError:
            logger.warning(
                "Timed out publishing notification to listener '%s' (%s)",
                listener_id,
                callback,
            )


def _listener_accepts_event(listener: HubListenerRecord, event_type: str) -> bool:
    """
    Supports a minimal query filter: eventType=... (single or comma separated).

    If query is absent or does not include eventType, deliver all notifications.
    """

    if listener.query is None or listener.query.strip() == "":
        return True

    raw_query = listener.query.lstrip("?")
    query_data = parse.parse_qs(raw_query, keep_blank_values=False)
    event_type_filters = query_data.get("eventType")
    if not event_type_filters:
        return True

    accepted_event_types: set[str] = set()
    for value in event_type_filters:
        for item in value.split(","):
            normalized = item.strip()
            if normalized:
                accepted_event_types.add(normalized)

    if not accepted_event_types:
        return True
    return event_type in accepted_event_types

