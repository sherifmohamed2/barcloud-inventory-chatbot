"""
Azure OpenAI concrete LLM client implementation.
"""

from openai import AzureOpenAI, RateLimitError, APIConnectionError

from src.app.domain.interface.llm_client_interface import LLMClientInterface
from src.app.infrastructure.errors import LLMConnectionError, LLMRateLimitError
from src.app.config import get_settings


class AzureClient(LLMClientInterface):
    """Azure OpenAI API client using structured output via beta.chat.completions.parse."""

    def __init__(self) -> None:
        cfg = get_settings()
        self._client = AzureOpenAI(
            azure_endpoint=cfg.azure_openai_endpoint,
            api_key=cfg.azure_openai_api_key,
            api_version="2024-02-01",
        )
        self._model = cfg.azure_openai_deployment
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
            raise LLMRateLimitError(provider="azure") from e
        except APIConnectionError as e:
            raise LLMConnectionError("Cannot reach Azure OpenAI", str(e)) from e

    def structured_chat(self, messages, structured_response, model=None, temperature=None):
        try:
            return self._client.beta.chat.completions.parse(
                model=model or self._model,
                messages=messages,
                response_format=structured_response,
                temperature=temperature if temperature is not None else self._temp,
                max_tokens=self._max_tokens,
            )
        except RateLimitError as e:
            raise LLMRateLimitError(provider="azure") from e
        except APIConnectionError as e:
            raise LLMConnectionError("Cannot reach Azure OpenAI", str(e)) from e
