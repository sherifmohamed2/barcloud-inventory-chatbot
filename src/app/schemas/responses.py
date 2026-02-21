"""
Outbound response schemas and LLM structured output contract.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Token usage breakdown from LLM completion."""

    prompt_tokens: int = Field(..., ge=0)
    completion_tokens: int = Field(..., ge=0)
    total_tokens: int = Field(..., ge=0)


class LLMResponseSchema(BaseModel):
    """
    Structured output contract passed to beta.chat.completions.parse().

    The LLM is constrained to return exactly these two fields.
    ChatService reads completion.choices[0].message.parsed → this type.
    """

    natural_language_answer: str = Field(
        ..., description="Human-readable answer to the user's question"
    )
    sql_query: str = Field(
        ..., description="SQL Server query that produces the answer (present query)"
    )


class ChatResponse(BaseModel):
    """Full outbound response for POST /api/chat."""

    session_id: str
    natural_language_answer: str
    sql_query: str
    token_usage: TokenUsage
    latency_ms: int = Field(..., ge=0)
    provider: Literal["openai", "azure"]
    model: str
    status: Literal["ok", "error"]
    error_detail: Optional[str] = None
