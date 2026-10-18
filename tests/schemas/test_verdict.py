import pytest
from pydantic import ValidationError

from parallax.schemas.verdict import Verdict, VerdictDecision


def test_valid_verdict_is_accepted() -> None:
    verdict = Verdict(
        decision=VerdictDecision.PROCEED,
        rationale=(
            "The proposal is feasible, addresses a clear need, "
            "and has manageable implementation risks."
        ),
        key_strengths=["Clear target audience"],
        key_concerns=["The rollout plan needs refinement"],
        recommendations=["Define milestones and measurable outcomes."],
    )

    assert verdict.decision == VerdictDecision.PROCEED
    assert len(verdict.recommendations) == 1


def test_invalid_decision_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Verdict(
            decision="maybe",
            rationale=("The proposal has some merits but needs a clear decision."),
            recommendations=["Clarify the project scope."],
        )


def test_rationale_cannot_be_too_short() -> None:
    with pytest.raises(ValidationError):
        Verdict(
            decision=VerdictDecision.REVISE,
            rationale="Needs work.",
            recommendations=["Define the missing requirements."],
        )


def test_recommendations_are_required() -> None:
    with pytest.raises(ValidationError):
        Verdict(
            decision=VerdictDecision.REJECT,
            rationale=("The proposal has fundamental problems that remain unresolved."),
            recommendations=[],
        )


def test_blank_recommendation_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Verdict(
            decision=VerdictDecision.REVISE,
            rationale=("The proposal has potential but needs significant refinement."),
            recommendations=["   "],
        )


def test_strengths_and_concerns_default_to_empty_lists() -> None:
    verdict = Verdict(
        decision=VerdictDecision.REVISE,
        rationale=("The proposal needs further development before implementation."),
        recommendations=["Clarify the requirements."],
    )

    assert verdict.key_strengths == []
    assert verdict.key_concerns == []


def test_unexpected_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        Verdict(
            decision=VerdictDecision.PROCEED,
            rationale=(
                "The proposal is feasible and its principal risks are manageable."
            ),
            recommendations=["Define measurable milestones."],
            unknown_field="unexpected",  # type: ignore
        )
