from functools import lru_cache

from openai import OpenAI

from parallax.config import get_settings


@lru_cache(maxsize=1)
def get_llm_client() -> OpenAI:
    settings = get_settings()

    return OpenAI(
        api_key=settings.openrouter_api_key.get_secret_value(),
        base_url=settings.openrouter_base_url,
        timeout=30.0,
        max_retries=0,
    )
