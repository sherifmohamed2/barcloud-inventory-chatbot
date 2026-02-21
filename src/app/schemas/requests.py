"""
Inbound request schemas.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class ChatRequest(BaseModel):
    """Inbound payload for POST /api/chat."""

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Client-generated session identifier (UUID recommended)",
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Natural language question from the user",
    )
    context: Optional[Dict[str, Any]] = Field(default=None)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("message must not be whitespace-only")
        return v.strip()

    @field_validator("session_id")
    @classmethod
    def session_id_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("session_id must not contain spaces")
        return v
