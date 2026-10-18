from pydantic import ValidationError

from parallax.agents.builder import (
    BuilderAgentError,
    build_proposal,
)


def main() -> None:
    idea = (
        "Build a web application for college students to "
        "manage study schedules, track completed sessions, "
        "and prepare for examinations."
    )

    try:
        proposal = build_proposal(idea)
    except (BuilderAgentError, ValidationError) as exc:
        print(f"Builder Agent failed: {exc}")
        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"LLM request failed: {type(exc).__name__}: {exc}")
        raise SystemExit(1) from exc

    print("\n=== BUILDER AGENT: LIVE RESULT ===")
    print(proposal.model_dump_json(indent=2))
    print("\nProposal validation: PASSED")


if __name__ == "__main__":
    main()
