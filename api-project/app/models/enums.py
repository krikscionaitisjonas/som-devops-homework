from enum import StrEnum


class ServiceOrderActionType(StrEnum):
    ADD = "add"
    MODIFY = "modify"
    DELETE = "delete"
    NO_CHANGE = "noChange"


class ServiceOrderStateType(StrEnum):
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "inProgress"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REJECTED = "rejected"
    PARTIAL = "partial"


class ServiceOrderItemStateType(StrEnum):
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "inProgress"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    REJECTED = "rejected"


class ServiceStateType(StrEnum):
    FEASIBILITY_CHECKED = "feasibilityChecked"
    DESIGNED = "designed"
    RESERVED = "reserved"
    INACTIVE = "inactive"
    ACTIVE = "active"
    TERMINATED = "terminated"

