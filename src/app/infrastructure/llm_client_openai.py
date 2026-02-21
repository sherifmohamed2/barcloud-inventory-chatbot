"""
OpenAI concrete LLM client implementation.
"""

from openai import OpenAI, RateLimitError, APIConnectionError

from src.app.domain.interface.llm_client_interface import LLMClientInterface
from src.app.infrastructure.errors import LLMConnectionError, LLMRateLimitError
from src.app.config import get_settings


class OpenAIClient(LLMClientInterface):
    """OpenAI API client using structured output via beta.chat.completions.parse."""

    def __init__(self) -> None:
        cfg = get_settings()
        self._client = OpenAI(api_key=cfg.openai_api_key)
        self._model = cfg.model_name
        self._temp = cfg.temperature
        self._max_tokens = cfg.max_tokens

    def chat(self, messages, model=None, temperature=None):
        try:
            return self._client.chat.completions.create(
                model=model or self._model,
                messages=messages,
                temperature=temperature if temperature is not None else self._temp,
                max_tokens=self._max_tokens,
            )
        except RateLimitError as e:
            raise LLMRateLimitError(provider="openai") from e
        except APIConnectionError as e:
            raise LLMConnectionError("Cannot reach OpenAI API", str(e)) from e

    def structured_chat(self, messages, structured_response, model=None, temperature=None):
        """
        Uses beta.chat.completions.parse to enforce structured output.

        structured_response is a Pydantic BaseModel class (e.g. LLMResponseSchema).
        Returns completion object — caller reads .choices[0].message.parsed.
        """
        try:
            return self._client.beta.chat.completions.parse(
                model=model or self._model,
                messages=messages,
                response_format=structured_response,
                temperature=temperature if temperature is not None else self._temp,
                max_tokens=self._max_tokens,
            )
        except RateLimitError as e:
            raise LLMRateLimitError(provider="openai") from e
        except APIConnectionError as e:
            raise LLMConnectionError("Cannot reach OpenAI API", str(e)) from e
