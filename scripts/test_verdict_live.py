from parallax.agents.architect import assess_proposal
from parallax.agents.skeptic import challenge_proposal
from parallax.agents.verdict import (
    evaluate_proposal,
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
        print("Running Architect Agent...")
        architect_assessment = assess_proposal(proposal)

        print("Running Skeptic Agent...")
        skeptic_assessment = challenge_proposal(proposal)

        print("Running Verdict Agent...")
        verdict = evaluate_proposal(
            proposal,
            architect_assessment,
            skeptic_assessment,
        )

    except Exception as exc:
        print(f"\nWorkflow failed: {type(exc).__name__}: {exc}")

        if exc.__cause__ is not None:
            print("\nUnderlying error:")
            print(exc.__cause__)

        raise SystemExit(1) from exc

    print("\n=== ARCHITECT ASSESSMENT ===")
    print(architect_assessment.model_dump_json(indent=2))

    print("\n=== SKEPTIC ASSESSMENT ===")
    print(skeptic_assessment.model_dump_json(indent=2))

    print("\n=== FINAL VERDICT ===")
    print(verdict.model_dump_json(indent=2))

    print("\nAll three live inference calls succeeded.")
    print("All outputs passed schema validation.")


if __name__ == "__main__":
    main()
