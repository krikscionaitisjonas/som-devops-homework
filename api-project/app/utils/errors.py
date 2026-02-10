class NotFoundError(Exception):
    """Raised when a requested resource does not exist."""


class ConflictError(Exception):
    """Raised when an operation conflicts with current state."""


class InvalidFilterError(Exception):
    """Raised when unsupported filter expressions are provided."""


class InvalidFieldSelectionError(Exception):
    """Raised when unsupported fields selection is provided."""

