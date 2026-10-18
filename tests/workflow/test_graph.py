
from unittest.mock import patch

from parallax.schemas.assessment import (
    AgentAssessment,
    AgentRole,
    Finding,
    Severity,
)
from parallax.schemas.proposal import Proposal
from parallax.schemas.verdict import Verdict, VerdictDecision
from parallax.workflow.graph import build_graph


def make_proposal() -> Proposal:
    return Proposal(
        title="Study Planner",
        description=(
            "A web application that helps students organize study "
            "sessions and track examination preparation."
        ),
        objective=(
            "Help students plan study sessions and monitor progress."
        ),
        constraints=["Use localStorage in the first version."],
        success_criteria=["Users can schedule and track study sessions."],
    )


def make_assessment(role: AgentRole) -> AgentAssessment:
    return AgentAssessment(
        agent=role,
        summary="The proposal is feasible but has some limitations.",
        findings=[
            Finding(
                title="Limited persistence",
                explanation=(
                    "Browser-only storage can cause data loss "
                    "if browser data is cleared."
                ),
                severity=Severity.MEDIUM,
                evidence=["The proposal uses localStorage."],
            )
        ],
        recommendations=["Add data export and import."],
    )


def make_verdict() -> Verdict:
    return Verdict(
        decision=VerdictDecision.REVISE,
        rationale=(
            "The proposal is feasible, but data recovery should be "
            "improved before the application is considered complete."
        ),
        key_strengths=["The initial scope is achievable."],
        key_concerns=["Browser-only storage can lose user data."],
        recommendations=["Implement JSON export and import."],
    )


def test_graph_runs_all_agents_and_returns_final_state() -> None:
    proposal = make_proposal()
    architect_assessment = make_assessment(AgentRole.ARCHITECT)
    skeptic_assessment = make_assessment(AgentRole.SKEPTIC)
    verdict = make_verdict()

    with (
        patch(
            "parallax.workflow.nodes.build_proposal",
            return_value=proposal,
        ) as builder,
        patch(
            "parallax.workflow.nodes.assess_proposal",
            return_value=architect_assessment,
        ) as architect,
        patch(
            "parallax.workflow.nodes.challenge_proposal",
            return_value=skeptic_assessment,
        ) as skeptic,
        patch(
            "parallax.workflow.nodes.evaluate_proposal",
            return_value=verdict,
        ) as evaluator,
    ):
        result = build_graph().invoke(
            {"user_idea": "Build a study planner"}
        )

    builder.assert_called_once_with("Build a study planner")
    architect.assert_called_once_with(proposal)
    skeptic.assert_called_once_with(proposal)
    evaluator.assert_called_once_with(
        proposal,
        architect_assessment,
        skeptic_assessment,
    )

    assert result["proposal"] == proposal
    assert result["architect_assessment"] == architect_assessment
    assert result["skeptic_assessment"] == skeptic_assessment
    assert result["verdict"] == verdict
