import json
from unittest.mock import MagicMock, patch

import pytest

from parallax.agents.verdict import (
    VerdictAgentError,
    evaluate_proposal,
)
from parallax.schemas.assessment import AgentAssessment
from parallax.schemas.proposal import Proposal
from parallax.schemas.verdict import Verdict, VerdictDecision


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


@pytest.fixture
def architect_assessment():
    return AgentAssessment(
        agent="architect",
        summary=("The proposal is technically feasible as a client-side MVP."),
        findings=[
            {
                "title": "Local storage limitations",
                "explanation": (
                    "Local storage does not provide automatic cloud backup."
                ),
                "severity": "medium",
                "evidence": ["The proposal specifies local browser storage."],
            }
        ],
        recommendations=["Add a data export mechanism."],
    )


@pytest.fixture
def skeptic_assessment():
    return AgentAssessment(
        agent="skeptic",
        summary=("The proposal has manageable risks around data loss."),
        findings=[
            {
                "title": "No recovery mechanism",
                "explanation": ("Users may lose data if browser storage is cleared."),
                "severity": "high",
                "evidence": ["The proposal excludes a backend."],
            }
        ],
        recommendations=["Provide data export and explain local storage limitations."],
    )


VALID_VERDICT = {
    "decision": "revise",
    "rationale": (
        "The proposal is feasible, but data loss is a significant "
        "risk that should be addressed before release."
    ),
    "key_strengths": ["The MVP has a clearly defined scope."],
    "key_concerns": ["Users may permanently lose locally stored study data."],
    "recommendations": ["Implement data export before releasing the MVP."],
}


def mock_model_response(content):
    response = MagicMock()
    response.choices[0].message.content = content
    return response


def run_with_mocked_llm(
    proposal,
    architect_assessment,
    skeptic_assessment,
    content,
):
    with (
        patch("parallax.agents.verdict.get_settings") as settings,
        patch("parallax.agents.verdict.get_llm_client") as get_client,
    ):
        settings.return_value.openrouter_model = (
            "nvidia/nemotron-3-ultra-550b-a55b:free"
        )
        get_client.return_value.chat.completions.create.return_value = (
            mock_model_response(content)
        )

        return evaluate_proposal(
            proposal,
            architect_assessment,
            skeptic_assessment,
        )


def test_evaluate_proposal_returns_valid_verdict(
    proposal,
    architect_assessment,
    skeptic_assessment,
):
    verdict = run_with_mocked_llm(
        proposal,
        architect_assessment,
        skeptic_assessment,
        json.dumps(VALID_VERDICT),
    )

    assert isinstance(verdict, Verdict)
    assert verdict.decision == VerdictDecision.REVISE
    assert len(verdict.recommendations) >= 1


def test_evaluate_proposal_rejects_empty_response(
    proposal,
    architect_assessment,
    skeptic_assessment,
):
    with pytest.raises(VerdictAgentError, match="empty verdict"):
        run_with_mocked_llm(
            proposal,
            architect_assessment,
            skeptic_assessment,
            None,
        )


def test_evaluate_proposal_rejects_malformed_json(
    proposal,
    architect_assessment,
    skeptic_assessment,
):
    with pytest.raises(VerdictAgentError, match="malformed JSON"):
        run_with_mocked_llm(
            proposal,
            architect_assessment,
            skeptic_assessment,
            '{"decision":',
        )


def test_evaluate_proposal_rejects_invalid_verdict(
    proposal,
    architect_assessment,
    skeptic_assessment,
):
    invalid = {
        **VALID_VERDICT,
        "decision": "maybe",
    }

    with pytest.raises(
        VerdictAgentError,
        match="failed validation",
    ):
        run_with_mocked_llm(
            proposal,
            architect_assessment,
            skeptic_assessment,
            json.dumps(invalid),
        )


def test_evaluate_proposal_rejects_wrong_architect_role(
    proposal,
    skeptic_assessment,
):
    with pytest.raises(
        ValueError,
        match="architect_assessment must belong",
    ):
        evaluate_proposal(
            proposal,
            skeptic_assessment,
            skeptic_assessment,
        )


def test_evaluate_proposal_rejects_wrong_skeptic_role(
    proposal,
    architect_assessment,
):
    with pytest.raises(
        ValueError,
        match="skeptic_assessment must belong",
    ):
        evaluate_proposal(
            proposal,
            architect_assessment,
            architect_assessment,
        )
