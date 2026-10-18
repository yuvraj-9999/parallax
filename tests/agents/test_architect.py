from unittest.mock import MagicMock, patch

import pytest

from parallax.agents.architect import (
    ArchitectAgentError,
    assess_proposal,
)
from parallax.schemas.assessment import AgentAssessment, AgentRole
from parallax.schemas.proposal import Proposal

VALID_ASSESSMENT = {
    "agent": "architect",
    "summary": (
        "The proposed application is feasible as a client-side MVP, "
        "although local persistence introduces limitations."
    ),
    "findings": [
        {
            "title": "Local storage limitations",
            "explanation": (
                "Browser localStorage supports a simple MVP but does "
                "not provide automatic cross-device synchronization."
            ),
            "severity": "medium",
            "evidence": ["The proposal specifies localStorage for persistence."],
        }
    ],
    "assumptions": ["The first version targets individual users on one device."],
    "recommendations": [
        "Consider data export to reduce the impact of local data loss."
    ],
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
        patch("parallax.agents.architect.get_settings") as settings,
        patch("parallax.agents.architect.get_llm_client") as get_client,
    ):
        settings.return_value.openrouter_model = (
            "nvidia/nemotron-3-ultra-550b-a55b:free"
        )
        get_client.return_value.chat.completions.create.return_value = (
            mock_model_response(content)
        )

        return assess_proposal(proposal)


def test_assess_proposal_returns_valid_assessment(proposal):
    import json

    assessment = run_with_mocked_llm(
        proposal,
        json.dumps(VALID_ASSESSMENT),
    )

    assert isinstance(assessment, AgentAssessment)
    assert assessment.agent == AgentRole.ARCHITECT
    assert assessment.findings[0].severity == "medium"


def test_assess_proposal_rejects_empty_response(proposal):
    with pytest.raises(ArchitectAgentError, match="empty assessment"):
        run_with_mocked_llm(proposal, None)


def test_assess_proposal_rejects_malformed_json(proposal):
    with pytest.raises(ArchitectAgentError, match="malformed JSON"):
        run_with_mocked_llm(proposal, '{"agent":')


def test_assess_proposal_rejects_invalid_assessment(proposal):
    import json

    invalid = {
        **VALID_ASSESSMENT,
        "findings": [],
    }

    with pytest.raises(
        ArchitectAgentError,
        match="failed validation",
    ):
        run_with_mocked_llm(proposal, json.dumps(invalid))


def test_assess_proposal_rejects_wrong_agent_role(proposal):
    import json

    wrong_role = {
        **VALID_ASSESSMENT,
        "agent": "skeptic",
    }

    with pytest.raises(
        ArchitectAgentError,
        match="wrong agent role",
    ):
        run_with_mocked_llm(proposal, json.dumps(wrong_role))
