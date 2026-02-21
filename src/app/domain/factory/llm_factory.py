"""
LLM provider factory.

Uses lazy imports to avoid circular dependencies at module load time.
"""

import importlib

from src.app.domain.interface.llm_client_interface import LLMClientInterface
from src.app.infrastructure.errors import InfrastructureError

_PROVIDER_MAP: dict[str, str] = {
    "openai": "src.app.infrastructure.llm_client_openai.OpenAIClient",
    "azure": "src.app.infrastructure.llm_client_azure.AzureClient",
}


def get_llm_client(provider: str) -> LLMClientInterface:
    """
    Factory: return the correct LLMClientInterface implementation
    for the given provider string.

    Uses lazy imports to avoid circular dependencies at module load time.
    Raises InfrastructureError for unknown providers.
    """
    dotted_path = _PROVIDER_MAP.get(provider.lower())
    if dotted_path is None:
        raise InfrastructureError(
            f"Unknown LLM provider: {provider!r}. Valid: {list(_PROVIDER_MAP)}"
        )
    module_path, class_name = dotted_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    klass = getattr(module, class_name)
    return klass()
