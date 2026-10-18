from unittest.mock import MagicMock, patch

import pytest

from parallax.agents.builder import (
    BuilderAgentError,
    build_proposal,
)
from parallax.schemas.proposal import Proposal

VALID_PROPOSAL_JSON = """
{
    "title": "Personal Study Planner",
    "description": "A web application that helps students plan study sessions and track their progress.",
    "objective": "Help students organize their study schedules and improve consistency.",
    "constraints": ["Must be usable on mobile devices"],
    "success_criteria": ["Users can create and track study sessions"]
}
"""


def test_build_proposal_returns_validated_proposal():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = VALID_PROPOSAL_JSON

    with (
        patch("parallax.agents.builder.get_settings") as mock_settings,
        patch("parallax.agents.builder.get_llm_client") as mock_client,
    ):
        mock_settings.return_value.openrouter_model = (
            "nvidia/nemotron-3-ultra-550b-a55b:free"
        )
        mock_client.return_value.chat.completions.create.return_value = mock_response

        proposal = build_proposal("Build a study planner")

    assert isinstance(proposal, Proposal)
    assert proposal.title == "Personal Study Planner"


def test_build_proposal_rejects_empty_idea():
    with pytest.raises(ValueError, match="cannot be empty"):
        build_proposal("   ")


def test_build_proposal_rejects_empty_model_response():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = None

    with (
        patch("parallax.agents.builder.get_settings"),
        patch("parallax.agents.builder.get_llm_client") as mock_client,
    ):
        mock_client.return_value.chat.completions.create.return_value = mock_response

        with pytest.raises(
            BuilderAgentError,
            match="empty response",
        ):
            build_proposal("Build a study planner")


def test_build_proposal_rejects_invalid_model_output():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"title": "Too short"}'

    with (
        patch("parallax.agents.builder.get_settings"),
        patch("parallax.agents.builder.get_llm_client") as mock_client,
    ):
        mock_settings = MagicMock()
        mock_settings.openrouter_model = "nvidia/nemotron-3-ultra-550b-a55b:free"
        mock_settings.openrouter_base_url = "https://openrouter.ai/api/v1"

        from parallax.agents import builder

        with patch.object(
            builder,
            "get_settings",
            return_value=mock_settings,
        ):
            mock_client.return_value.chat.completions.create.return_value = (
                mock_response
            )

            with pytest.raises(
                BuilderAgentError,
                match="failed validation",
            ):
                build_proposal("Build a study planner")


def test_build_proposal_rejects_malformed_json():
    mock_response = MagicMock()
    mock_response.choices[0].message.content = '{"title":'

    with (
        patch("parallax.agents.builder.get_settings") as mock_settings,
        patch("parallax.agents.builder.get_llm_client") as mock_client,
    ):
        mock_settings.return_value.openrouter_model = (
            "nvidia/nemotron-3-ultra-550b-a55b:free"
        )
        mock_client.return_value.chat.completions.create.return_value = mock_response

        with pytest.raises(
            BuilderAgentError,
            match="malformed JSON",
        ):
            build_proposal("Build a study planner")
