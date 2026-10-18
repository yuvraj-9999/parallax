from parallax.agents.architect import (
    ArchitectAgentError,
    assess_proposal,
)
from parallax.schemas.proposal import Proposal


def main() -> None:
    proposal = Proposal(
        title="Study Planner",
        description=(
            "A responsive web application for college students "
            "to manage study schedules, record completed sessions, "
            "and track examination preparation."
        ),
        objective=(
            "Help students organize their study schedules "
            "and monitor their learning progress."
        ),
        constraints=[
            "The first version uses browser localStorage.",
            "No backend or authentication is included.",
            "The initial budget is zero.",
        ],
        success_criteria=[
            "Users can schedule study sessions.",
            "Users can track completed sessions.",
            "Study data persists across browser sessions.",
        ],
    )

    try:
        assessment = assess_proposal(proposal)
    except ArchitectAgentError as exc:
        print(f"Architect Agent failed: {exc}")

        if exc.__cause__ is not None:
            print("\nUnderlying error:")
            print(exc.__cause__)

        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"LLM request failed: {type(exc).__name__}: {exc}")
        raise SystemExit(1) from exc

    print("\n=== ARCHITECT AGENT: LIVE RESULT ===")
    print(assessment.model_dump_json(indent=2))
    print("\nAssessment validation: PASSED")


if __name__ == "__main__":
    main()
