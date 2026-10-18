from functools import lru_cache

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openrouter_api_key: SecretStr
    openrouter_model: str
    openrouter_base_url: str = Field(default="https://openrouter.ai/api/v1")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @field_validator("openrouter_model")
    @classmethod
    def validate_model(cls, value: str) -> str:
        value = value.strip()

        if value != "openrouter/free" and not value.endswith(":free"):
            raise ValueError(
                "Only openrouter/free or explicitly free model IDs are allowed."
            )

        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
