"""
ChatService — business logic orchestrator.

Depends on LLMClientInterface — never on concrete provider classes.
All exceptions are caught here; status="error" responses are returned instead.
"""

from __future__ import annotations

import logging
import time

from src.app.domain.interface.llm_client_interface import LLMClientInterface
from src.app.infrastructure.session_store import InMemorySessionStore
from src.app.infrastructure.clock import UTCClock
from src.app.schemas import LLMResponseSchema, ChatResponse, TokenUsage
from src.app.constants import SYSTEM_PROMPT
from src.app.domain.conversation import build_messages, trim_history
from src.app.domain.intent_detection import resolve
from src.app.domain.errors import BarCloudError
from src.app.domain.sql_safety import validate_sql_readonly
from src.app.config import get_settings


class ChatService:
    """
    Business logic orchestrator.

    Depends on LLMClientInterface — never on concrete provider classes.
    All exceptions are caught here; status="error" responses are returned instead.
    """

    def __init__(
        self,
        llm_client: LLMClientInterface,
        session_store: InMemorySessionStore,
        clock: UTCClock | None = None,
    ) -> None:
        self._llm = llm_client
        self._store = session_store
        self._clock = clock or UTCClock()
        self._provider = get_settings().provider
        self._model = get_settings().model_name
        self._logger = logging.getLogger(__name__)

    def get_chat_response(self, session_id: str, message: str) -> ChatResponse:
        """
        Main entry point. Returns ChatResponse with status="error" on failure.
        Never raises exceptions to the caller.
        """
        t_start = time.perf_counter()
        try:
            return self._process(session_id, message, t_start)
        except BarCloudError as exc:
            self._logger.error("Handled error: %s", exc, exc_info=True)
            return self._error_response(session_id, exc, t_start)
        except Exception as exc:
            self._logger.critical("Unexpected error: %s", exc, exc_info=True)
            return self._error_response(
                session_id,
                BarCloudError("Internal server error", str(exc)),
                t_start,
            )

    def _process(
        self, session_id: str, message: str, t_start: float
    ) -> ChatResponse:
        # 1. Load session history
        history = self._store.get(session_id)

        # 2. Append user message
        history = list(history)
        history.append({"role": "user", "content": message})

        # 3. Trim history to max turns
        history = trim_history(history)

        # 4. Build full messages list
        messages = build_messages(SYSTEM_PROMPT, history)

        # 5. Call LLM with structured output
        completion = self._llm.structured_chat(
            messages=messages,
            structured_response=LLMResponseSchema,
        )

        # 6. Parse typed result — no json.loads() needed
        parsed: LLMResponseSchema = completion.choices[0].message.parsed
        usage = completion.usage

        # 7. Validate SQL is read-only (no DROP, DELETE, etc.)
        if parsed.sql_query:
            validate_sql_readonly(parsed.sql_query)

        # 8. Get SQL query for the detected intent
        # LLM provides answer + sql directly via structured output
        # intent detection provides the enum for audit/logging
        intent = resolve(
            parsed.sql_query[:30] if parsed.sql_query else "unknown"
        )
        sql_query = parsed.sql_query or ""

        # 9. Append assistant response to history
        history.append(
            {"role": "assistant", "content": parsed.natural_language_answer}
        )

        # 10. Save updated session
        self._store.save(session_id, history)

        latency_ms = int((time.perf_counter() - t_start) * 1000)

        return ChatResponse(
            session_id=session_id,
            natural_language_answer=parsed.natural_language_answer,
            sql_query=sql_query,
            token_usage=TokenUsage(
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
            ),
            latency_ms=latency_ms,
            provider=self._provider,
            model=self._model,
            status="ok",
        )

    def _error_response(
        self, session_id: str, exc: BarCloudError, t_start: float
    ) -> ChatResponse:
        return ChatResponse(
            session_id=session_id,
            natural_language_answer="An error occurred. Please try again.",
            sql_query="",
            token_usage=TokenUsage(
                prompt_tokens=0, completion_tokens=0, total_tokens=0
            ),
            latency_ms=int((time.perf_counter() - t_start) * 1000),
            provider=self._provider,
            model=self._model,
            status="error",
            error_detail=exc.message,
        )
