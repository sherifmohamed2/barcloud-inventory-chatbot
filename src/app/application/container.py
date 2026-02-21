"""
Dependency Injection container.

This is the ONLY file in the project that imports concrete infrastructure classes.
All other files depend on abstractions.
"""

from __future__ import annotations

from src.app.domain.factory.llm_factory import get_llm_client
from src.app.infrastructure.session_store import InMemorySessionStore
from src.app.infrastructure.clock import UTCClock
from src.app.services.chat_service import ChatService
from src.app.config import get_settings

# Module-level singletons (built once per process)
_chat_service: ChatService | None = None


def get_chat_service() -> ChatService:
    """
    DI root. Builds and caches the full service graph.

    Called by presentation/handlers.py — which never imports
    OpenAIClient, AzureClient, InMemorySessionStore, or UTCClock directly.
    """
    global _chat_service
    if _chat_service is None:
        cfg = get_settings()
        llm_client = get_llm_client(cfg.provider)
        session_store = InMemorySessionStore(max_sessions=cfg.max_sessions)
        clock = UTCClock()
        _chat_service = ChatService(
            llm_client=llm_client,
            session_store=session_store,
            clock=clock,
        )
    return _chat_service
