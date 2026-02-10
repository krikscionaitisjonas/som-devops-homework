from datetime import datetime
from typing import Literal

from pydantic import Field

from app.models.common import TMFBaseModel
from app.models.service_order import ServiceOrder


class ServiceOrderEvent(TMFBaseModel):
    service_order: ServiceOrder = Field(alias="serviceOrder")


class ServiceOrderNotification(TMFBaseModel):
    event_id: str = Field(alias="eventId")
    event_time: datetime = Field(alias="eventTime")
    event_type: str = Field(alias="eventType")
    event: ServiceOrderEvent


class ServiceOrderCreateNotification(ServiceOrderNotification):
    event_type: Literal["ServiceOrderCreateNotification"] = Field(
        default="ServiceOrderCreateNotification", alias="eventType"
    )


class ServiceOrderAttributeValueChangeNotification(ServiceOrderNotification):
    event_type: Literal["ServiceOrderAttributeValueChangeNotification"] = Field(
        default="ServiceOrderAttributeValueChangeNotification", alias="eventType"
    )


class ServiceOrderStateChangeNotification(ServiceOrderNotification):
    event_type: Literal["ServiceOrderStateChangeNotification"] = Field(
        default="ServiceOrderStateChangeNotification", alias="eventType"
    )


class ServiceOrderDeleteNotification(ServiceOrderNotification):
    event_type: Literal["ServiceOrderDeleteNotification"] = Field(
        default="ServiceOrderDeleteNotification", alias="eventType"
    )

