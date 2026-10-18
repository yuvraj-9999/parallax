import json
from unittest.mock import MagicMock, patch

import pytest

from parallax.agents.skeptic import (
    SkepticAgentError,
    challenge_proposal,
)
from parallax.schemas.assessment import AgentAssessment, AgentRole
from parallax.schemas.proposal import Proposal

VALID_ASSESSMENT = {
    "agent": "skeptic",
    "summary": (
        "The proposal is promising, but several assumptions "
        "and data-loss risks require attention."
    ),
    "findings": [
        {
            "title": "No recovery mechanism",
            "explanation": (
                "The proposal relies on local browser storage without "
                "a defined recovery mechanism if the data is lost."
            ),
            "severity": "high",
            "evidence": [
                "The proposal specifies localStorage for persistence.",
                "The proposal excludes a backend.",
            ],
        }
    ],
    "assumptions": ["Users will keep using the same browser and device."],
    "recommendations": ["Add data export and document the limits of local storage."],
}


@pytest.fixture
def proposal():
    return Proposal(
        title="Study Planner",
        description=(
            "A web application that helps students plan study sessions "
            "and track their progress."
        ),
        objective=("Help students organize their study schedules consistently."),
        constraints=["No backend in the first version"],
        success_criteria=["Users can schedule study sessions"],
    )


def mock_model_response(content):
    response = MagicMock()
    response.choices[0].message.content = content
    return response


def run_with_mocked_llm(proposal, content):
    with (
        patch("parallax.agents.skeptic.get_settings") as settings,
        patch("parallax.agents.skeptic.get_llm_client") as get_client,
    ):
        settings.return_value.openrouter_model = (
            "nvidia/nemotron-3-ultra-550b-a55b:free"
        )
        get_client.return_value.chat.completions.create.return_value = (
            mock_model_response(content)
        )

        return challenge_proposal(proposal)


def test_challenge_proposal_returns_valid_assessment(proposal):
    assessment = run_with_mocked_llm(
        proposal,
        json.dumps(VALID_ASSESSMENT),
    )

    assert isinstance(assessment, AgentAssessment)
    assert assessment.agent == AgentRole.SKEPTIC
    assert assessment.findings[0].severity == "high"


def test_challenge_proposal_rejects_empty_response(proposal):
    with pytest.raises(SkepticAgentError, match="empty assessment"):
        run_with_mocked_llm(proposal, None)


def test_challenge_proposal_rejects_malformed_json(proposal):
    with pytest.raises(SkepticAgentError, match="malformed JSON"):
        run_with_mocked_llm(proposal, '{"agent":')


def test_challenge_proposal_rejects_invalid_assessment(proposal):
    invalid = {
        **VALID_ASSESSMENT,
        "findings": [],
    }

    with pytest.raises(
        SkepticAgentError,
        match="failed validation",
    ):
        run_with_mocked_llm(proposal, json.dumps(invalid))


def test_challenge_proposal_rejects_wrong_agent_role(proposal):
    wrong_role = {
        **VALID_ASSESSMENT,
        "agent": "architect",
    }

    with pytest.raises(
        SkepticAgentError,
        match="wrong agent role",
    ):
        run_with_mocked_llm(proposal, json.dumps(wrong_role))
