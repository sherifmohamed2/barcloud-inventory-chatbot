"""
Resolve raw LLM intent strings to Intent enum values.
"""

import logging

from src.app.domain.intents_enum import IntentEnum

logger = logging.getLogger(__name__)


def resolve(raw_intent: str) -> IntentEnum:
    """
    Convert a raw string from LLM output to an Intent enum value.

    Falls back to Intent.UNKNOWN on unknown strings (never raises to caller).
    Logs a warning when falling back.
    """
    try:
        return IntentEnum(raw_intent)
    except ValueError:
        logger.warning(
            "Unknown intent %r — falling back to UNKNOWN", raw_intent
        )
        return IntentEnum.UNKNOWN
