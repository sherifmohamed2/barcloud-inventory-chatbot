"""
Abstract LLM client interface.

Services depend on this — never on concrete implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

ResponseFormatT = TypeVar("ResponseFormatT", bound=type[BaseModel])


class LLMClientInterface(ABC):
    """
    Abstract interface for all LLM provider clients.

    Services depend on this — never on concrete implementations.
    """

    @abstractmethod
    def chat(
        self,
        messages: list[dict],
        model: str | None = None,
        temperature: float | None = None,
    ) -> object:
        """Free-form chat completion. Returns raw completion object."""

    @abstractmethod
    def structured_chat(
        self,
        messages: list[dict],
        structured_response: ResponseFormatT,
        model: str | None = None,
        temperature: float | None = None,
    ) -> object:
        """
        Structured-output completion.

        structured_response: a Pydantic BaseModel subclass (e.g. LLMResponseSchema).
        Returns completion object — caller reads .choices[0].message.parsed.
        """
