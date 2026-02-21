"""
Service-layer exceptions.
"""

from src.app.domain.errors import BarCloudError


class ServiceError(BarCloudError):
    """Base for all service-layer exceptions."""


class SessionLimitExceededError(ServiceError):
    """Raised when the maximum number of sessions is reached."""

    def __init__(self, limit: int) -> None:
        self.limit = limit
        super().__init__(
            f"Session limit exceeded: {limit}",
            detail=f"Maximum sessions allowed: {limit}",
        )


class SessionNotFoundError(ServiceError):
    """Raised when a session_id does not exist."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        super().__init__(
            f"Session not found: {session_id!r}",
            detail=f"session_id: {session_id!r}",
        )
