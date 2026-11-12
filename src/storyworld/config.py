from pathlib import Path
from typing import Literal

from pydantic import model_validator
from pydantic.types import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="STORYWORLD_", env_file=".env")

    text_provider: Literal["mock", "gemini", "ollama"] = "mock"
    image_provider: Literal["mock", "hf", "pollinations"] = "mock"
    gemini_api_key: SecretStr | None = None
    hf_token: SecretStr | None = None
    pollinations_token: SecretStr | None = None
    ollama_base_url: str = "http://localhost:11434"
    data_dir: Path = Path("data")
    max_panels: int = 12
    max_dialogue_chars: int = 120

    @model_validator(mode="after")
    def _check_provider_credentials(self) -> "Settings":
        if self.text_provider == "gemini" and not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY est requis quand text_provider=gemini")
        if self.image_provider == "hf" and not self.hf_token:
            raise ValueError("HF_TOKEN est requis quand image_provider=hf")
        return self


def get_settings() -> Settings:
    return Settings()
