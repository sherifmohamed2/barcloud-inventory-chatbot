"""
In-memory session history store.

Interface-ready: to swap for Redis, replace this class with a
RedisSessionStore that has the same public methods — no changes
needed in services.
"""

import logging

logger = logging.getLogger(__name__)


class InMemorySessionStore:
    """In-memory session history store with FIFO eviction."""

    def __init__(self, max_sessions: int = 1000) -> None:
        self._sessions: dict[str, list[dict]] = {}
        self._max = max_sessions

    def get(self, session_id: str) -> list[dict]:
        """Return history for session_id. Returns [] if not found."""
        return self._sessions.get(session_id, [])

    def save(self, session_id: str, history: list[dict]) -> None:
        """
        Persist history for session_id.

        If max_sessions is reached, evict the oldest session (FIFO).
        """
        if session_id not in self._sessions:
            if len(self._sessions) >= self._max:
                oldest = next(iter(self._sessions))
                del self._sessions[oldest]
                logger.warning(
                    "Session limit (%d) reached — evicted session %s",
                    self._max,
                    oldest,
                )
        self._sessions[session_id] = history

    def delete(self, session_id: str) -> None:
        """Remove a session. No-op if not found."""
        self._sessions.pop(session_id, None)

    def count(self) -> int:
        return len(self._sessions)
