"""
Base exception hierarchy for the BarCloud Inventory Chatbot.

All custom exceptions in the project inherit from BarCloudError.
"""

from __future__ import annotations


class BarCloudError(Exception):
    """Base exception for all BarCloud errors."""

    def __init__(self, message: str, detail: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={self.message!r}, detail={self.detail!r})"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

class ConfigurationError(BarCloudError):
    """Raised when required configuration (env vars) is missing or invalid."""


# ---------------------------------------------------------------------------
# Domain errors
# ---------------------------------------------------------------------------

class DomainError(BarCloudError):
    """Base for all domain-layer exceptions."""


class IntentNotFoundError(DomainError):
    """Raised when an intent string cannot be resolved to an Intent enum value."""

    def __init__(self, received: str) -> None:
        self.received = received
        super().__init__(
            f"Intent not found: {received!r}",
            detail=f"Received value: {received!r}",
        )


class SQLValidationError(DomainError):
    """Raised when a SQL template is empty or missing for a given intent."""

    def __init__(self, intent: str) -> None:
        self.intent = intent
        super().__init__(
            f"SQL template missing or empty for intent: {intent!r}",
            detail=f"Intent: {intent!r}",
        )


class UnsafeSQLError(DomainError):
    """Raised when a SQL query is not read-only (e.g. DROP, DELETE, TRUNCATE)."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(
            "Query not allowed: only read-only (SELECT) queries are permitted.",
            detail=reason,
        )
