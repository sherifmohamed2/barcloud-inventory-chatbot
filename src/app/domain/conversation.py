"""
Conversation history management helpers.
"""

from src.app.constants import MAX_HISTORY_TURNS


def trim_history(
    history: list[dict], max_turns: int = MAX_HISTORY_TURNS
) -> list[dict]:
    """
    Trim conversation history to at most *max_turns* turns.

    A "turn" is one user + one assistant message (2 entries).
    Returns a new list (does not mutate the original).
    """
    max_entries = max_turns * 2
    if len(history) > max_entries:
        return history[-max_entries:]
    return list(history)


def build_messages(system_prompt: str, history: list[dict]) -> list[dict]:
    """Prepend the system prompt to the conversation history."""
    return [{"role": "system", "content": system_prompt}] + history
