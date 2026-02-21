"""
Infrastructure-layer exceptions.
"""

from __future__ import annotations

from src.app.domain.errors import BarCloudError


class InfrastructureError(BarCloudError):
    """Base for all infrastructure-layer exceptions."""


# ---------------------------------------------------------------------------
# LLM errors
# ---------------------------------------------------------------------------

class LLMError(InfrastructureError):
    """Base for LLM provider errors."""


class LLMConnectionError(LLMError):
    """Raised on network / authentication failure with LLM provider."""


class LLMRateLimitError(LLMError):
    """Raised when LLM provider returns 429 / quota exceeded."""

    def __init__(self, provider: str, retry_after: int | None = None) -> None:
        self.provider = provider
        self.retry_after = retry_after
        detail = f"Retry after {retry_after}s" if retry_after else None
        super().__init__(
            f"Rate limit exceeded for provider: {provider}",
            detail=detail,
        )


class LLMResponseParseError(LLMError):
    """Raised when LLM completion cannot be parsed into the expected schema."""

    def __init__(self, raw_response: str) -> None:
        self.raw_response = raw_response
        super().__init__(
            "Failed to parse LLM response",
            detail=f"Raw: {raw_response[:200]!r}",
        )


# ---------------------------------------------------------------------------
# Storage errors
# ---------------------------------------------------------------------------

class StorageError(InfrastructureError):
    """Raised on session store failure."""
