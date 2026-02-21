"""
Application settings via pydantic-settings BaseSettings.

Reads from environment variables and .env file.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings

from src.app.domain.errors import ConfigurationError


class Settings(BaseSettings):
    """BarCloud Inventory Chatbot configuration."""

    provider: Literal["openai", "azure"] = "openai"
    openai_api_key: str = ""
    model_name: str = "gpt-4o-mini"
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""
    host: str = "0.0.0.0"
    port: int = 8000
    max_sessions: int = 1000
    temperature: float = 0.0
    max_tokens: int = 512

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
    }

    @model_validator(mode="after")
    def validate_credentials(self) -> "Settings":
        if self.provider == "openai" and not self.openai_api_key:
            raise ConfigurationError(
                "OPENAI_API_KEY is required when PROVIDER=openai"
            )
        if self.provider == "azure":
            missing = []
            if not self.azure_openai_endpoint:
                missing.append("AZURE_OPENAI_ENDPOINT")
            if not self.azure_openai_api_key:
                missing.append("AZURE_OPENAI_API_KEY")
            if not self.azure_openai_deployment:
                missing.append("AZURE_OPENAI_DEPLOYMENT")
            if missing:
                raise ConfigurationError(
                    f"Missing Azure credentials: {', '.join(missing)}"
                )
        return self


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Return cached Settings singleton."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
