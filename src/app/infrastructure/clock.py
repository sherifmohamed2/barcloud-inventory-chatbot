"""
UTC clock abstraction.

Inject this instead of calling datetime.now() directly
so tests can substitute a fake clock.
"""

from datetime import datetime, timezone


class UTCClock:
    """Abstraction over datetime.now()."""

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def timestamp_ms(self) -> int:
        """Current UTC time as milliseconds since epoch."""
        return int(self.now().timestamp() * 1000)
