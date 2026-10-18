import pytest
from pydantic import ValidationError

from parallax.schemas.proposal import Proposal


def test_valid_proposal_is_accepted() -> None:
    proposal = Proposal(
        title="Build a campus study planner",
        description=(
            "A web application that helps students organize study sessions "
            "and track their academic progress."
        ),
        objective="Help students plan and complete study sessions.",
        constraints=["Must use free-tier services"],
        success_criteria=["Students can create and track study sessions"],
    )

    assert proposal.title == "Build a campus study planner"
    assert len(proposal.success_criteria) == 1


def test_title_is_trimmed() -> None:
    proposal = Proposal(
        title="  Study Planner  ",
        description=(
            "A web application for organizing study sessions and tracking "
            "academic progress throughout the semester."
        ),
        objective="Help students plan and complete study sessions.",
        success_criteria=["Users can create study sessions"],
    )

    assert proposal.title == "Study Planner"


def test_blank_title_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Proposal(
            title="   ",
            description=(
                "A web application for organizing study sessions and "
                "tracking academic progress."
            ),
            objective="Help students plan study sessions effectively.",
            success_criteria=["Users can create sessions"],
        )


def test_success_criteria_are_required() -> None:
    with pytest.raises(ValidationError):
        Proposal(
            title="Study Planner",
            description=(
                "A web application for organizing study sessions and "
                "tracking academic progress."
            ),
            objective="Help students plan study sessions effectively.",
            success_criteria=[],
        )


def test_unexpected_fields_are_rejected() -> None:
    with pytest.raises(ValidationError):
        Proposal(
            title="Study Planner",
            description=(
                "A web application for organizing study sessions and "
                "tracking academic progress."
            ),
            objective="Help students plan study sessions effectively.",
            success_criteria=["Users can create sessions"],
            unknown_field="unexpected",  # type: ignore[call-arg]
        )