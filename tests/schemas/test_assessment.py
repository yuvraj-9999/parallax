import pytest
from pydantic import ValidationError

from parallax.schemas.assessment import (
    AgentAssessment,
    AgentRole,
    Finding,
    Severity,
)


def test_valid_assessment_is_accepted() -> None:
    assessment = AgentAssessment(
        agent=AgentRole.BUILDER,
        summary="The proposal is feasible within the available resources.",
        findings=[
            Finding(
                title="Manageable implementation scope",
                explanation=(
                    "The required functionality can be implemented "
                    "using established technologies."
                ),
                severity=Severity.LOW,
                evidence=["The proposal uses an existing framework."],
            )
        ],
        recommendations=["Define milestones before implementation."],
    )

    assert assessment.agent == AgentRole.BUILDER
    assert assessment.findings[0].severity == Severity.LOW


def test_invalid_agent_role_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AgentAssessment(
            agent="unknown_agent",
            summary="The proposal needs further analysis.",
            findings=[
                Finding(
                    title="Missing implementation details",
                    explanation=("The proposal does not explain its architecture."),
                    severity=Severity.MEDIUM,
                )
            ],
            recommendations=["Document the proposed architecture."],
        )


def test_invalid_severity_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Finding(
            title="Missing technical details",
            explanation="The implementation approach is not explained.",
            severity="extreme",
        )


def test_assessment_requires_findings() -> None:
    with pytest.raises(ValidationError):
        AgentAssessment(
            agent=AgentRole.SKEPTIC,
            summary="The proposal requires additional scrutiny.",
            findings=[],
            recommendations=["Clarify the assumptions."],
        )


def test_assessment_requires_recommendations() -> None:
    with pytest.raises(ValidationError):
        AgentAssessment(
            agent=AgentRole.ARCHITECT,
            summary="The proposal requires a clearer design.",
            findings=[
                Finding(
                    title="Missing architecture",
                    explanation=(
                        "The proposal does not specify its system components."
                    ),
                    severity=Severity.MEDIUM,
                )
            ],
            recommendations=[],
        )


def test_evidence_and_assumptions_default_to_empty_lists() -> None:
    finding = Finding(
        title="Missing technical details",
        explanation="The implementation approach is not explained.",
        severity=Severity.MEDIUM,
    )

    assessment = AgentAssessment(
        agent=AgentRole.SKEPTIC,
        summary="The proposal requires additional scrutiny.",
        findings=[finding],
        recommendations=["Clarify the implementation approach."],
    )

    assert finding.evidence == []
    assert assessment.assumptions == []


def test_blank_finding_title_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Finding(
            title="   ",
            explanation="The implementation approach is not explained.",
            severity=Severity.MEDIUM,
        )


def test_blank_recommendation_is_rejected() -> None:
    with pytest.raises(ValidationError):
        AgentAssessment(
            agent=AgentRole.BUILDER,
            summary="The proposal is feasible with minor adjustments.",
            findings=[
                Finding(
                    title="Limited implementation scope",
                    explanation=(
                        "The proposed functionality uses familiar technologies."
                    ),
                    severity=Severity.LOW,
                )
            ],
            recommendations=["   "],
        )


def test_unexpected_finding_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        Finding(
            title="Unclear objective",
            explanation="The expected outcome is not adequately defined.",
            severity=Severity.MEDIUM,
            unexpected_field="not allowed",  # type: ignore
        )
