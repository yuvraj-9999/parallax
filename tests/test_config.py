import pytest
from pydantic import ValidationError

from parallax.config import Settings


def test_settings_accept_valid_configuration() -> None:
    settings = Settings(
        openrouter_api_key="test-key",
        openrouter_model="nvidia/nemotron-3-ultra-550b-a55b:free",
    )

    assert (
        settings.openrouter_model
        == "nvidia/nemotron-3-ultra-550b-a55b:free"
    )
    assert (
        settings.openrouter_base_url
        == "https://openrouter.ai/api/v1"
    )


def test_settings_reject_empty_model() -> None:
    with pytest.raises(ValidationError):
        Settings(
            openrouter_api_key="test-key",
            openrouter_model="",
        )


def test_settings_reject_paid_model() -> None:
    with pytest.raises(ValidationError):
        Settings(
            openrouter_api_key="test-key",
            openrouter_model="some-provider/paid-model",
        )


def test_api_key_is_masked() -> None:
    settings = Settings(
        openrouter_api_key="test-key",
        openrouter_model="nvidia/nemotron-3-ultra-550b-a55b:free",
    )

    assert str(settings.openrouter_api_key) == "**********"