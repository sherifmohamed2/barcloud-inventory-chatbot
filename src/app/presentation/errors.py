"""
Presentation-layer exceptions and HTTP error mapping.
"""

from src.app.domain.errors import BarCloudError


class PresentationError(BarCloudError):
    """Base for all presentation-layer exceptions."""


class RequestError(PresentationError):
    """Raised for malformed HTTP request bodies."""

    def __init__(self, detail: str) -> None:
        super().__init__("Invalid request", detail=detail)


def map_exception_to_http(exc: Exception) -> tuple[int, dict]:
    """Map an exception to an HTTP status code and JSON error body."""
    if isinstance(exc, RequestError):
        return 400, {
            "status": "error",
            "message": exc.message,
            "detail": exc.detail,
        }

    # Pydantic ValidationError
    try:
        from pydantic import ValidationError
        if isinstance(exc, ValidationError):
            return 422, {
                "status": "error",
                "message": "Validation failed",
                "detail": "; ".join(e["msg"] for e in exc.errors()),
            }
    except ImportError:
        pass

    return 500, {
        "status": "error",
        "message": "Internal server error",
    }
