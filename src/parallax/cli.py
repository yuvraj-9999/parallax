from parallax.schemas.assessment import AgentAssessment
from parallax.schemas.proposal import Proposal
from parallax.schemas.verdict import Verdict
from parallax.workflow.runner import WorkflowError, run_workflow

SEPARATOR = "=" * 72
SECTION_SEPARATOR = "-" * 72


def print_header(title: str) -> None:
    """Print a consistent section header."""

    print(f"\n{SEPARATOR}")
    print(title.upper())
    print(SEPARATOR)


def print_list(items: list[str], empty_message: str) -> None:
    """Print a list of strings in a readable numbered format."""

    if not items:
        print(f"  {empty_message}")
        return

    for index, item in enumerate(items, start=1):
        print(f"  {index}. {item}")


def display_proposal(proposal: Proposal) -> None:
    """Display the complete generated proposal."""

    print_header("Generated Proposal")

    print(f"\nTitle: {proposal.title}")
    print(f"\nDescription:\n{proposal.description}")
    print(f"\nObjective:\n{proposal.objective}")

    print("\nConstraints:")
    if proposal.constraints:
        for constraint in proposal.constraints:
            print(f"  - {constraint}")
    else:
        print("  None specified.")

    print("\nSuccess Criteria:")
    print_list(
        proposal.success_criteria,
        "None specified.",
    )


def display_assessment(assessment: AgentAssessment) -> None:
    """Display an agent assessment without exposing raw JSON."""

    print_header(f"{assessment.agent.value} Assessment")

    print(f"\nSummary:\n{assessment.summary}")

    print("\nFindings:")
    if not assessment.findings:
        print("  No findings reported.")

    for index, finding in enumerate(assessment.findings, start=1):
        print(f"\n  {index}. {finding.title}")
        print(f"     Severity: {finding.severity.value.upper()}")
        print(f"     Explanation: {finding.explanation}")

        print("     Evidence:")
        if finding.evidence:
            for evidence in finding.evidence:
                print(f"       - {evidence}")
        else:
            print("       No supporting evidence provided.")

    print("\nAssumptions:")
    print_list(
        assessment.assumptions,
        "None identified.",
    )

    print("\nRecommendations:")
    print_list(
        assessment.recommendations,
        "None provided.",
    )


def display_verdict(verdict: Verdict) -> None:
    """Display the final decision and its supporting reasoning."""

    print_header("Final Verdict")

    print(f"\nDecision: {verdict.decision.value.upper()}")
    print(f"\nRationale:\n{verdict.rationale}")

    print("\nKey Strengths:")
    print_list(
        verdict.key_strengths,
        "None identified.",
    )

    print("\nKey Concerns:")
    print_list(
        verdict.key_concerns,
        "None identified.",
    )

    print("\nRecommendations:")
    print_list(
        verdict.recommendations,
        "None provided.",
    )

    print(f"\n{SEPARATOR}")
    print("END OF EVALUATION")
    print(SEPARATOR)


def display_report(result: dict) -> None:
    """Display the complete workflow result in a readable format."""

    proposal = result.get("proposal")
    architect_assessment = result.get("architect_assessment")
    skeptic_assessment = result.get("skeptic_assessment")
    verdict = result.get("verdict")

    if not isinstance(proposal, Proposal):
        raise WorkflowError(
            "The workflow did not produce a valid proposal."
        )

    if not isinstance(architect_assessment, AgentAssessment):
        raise WorkflowError(
            "The workflow did not produce a valid Architect assessment."
        )

    if not isinstance(skeptic_assessment, AgentAssessment):
        raise WorkflowError(
            "The workflow did not produce a valid Skeptic assessment."
        )

    if not isinstance(verdict, Verdict):
        raise WorkflowError(
            "The workflow did not produce a valid final verdict."
        )

    display_proposal(proposal)
    display_assessment(architect_assessment)
    display_assessment(skeptic_assessment)
    display_verdict(verdict)


def main() -> None:
    """Run Parallax from the terminal."""

    print(SEPARATOR)
    print("PARALLAX")
    print("MULTI-AGENT PROPOSAL EVALUATION SYSTEM")
    print(SEPARATOR)

    print(
        "\nDescribe an idea you want evaluated. "
        "Parallax will generate a proposal, assess it from "
        "two perspectives, and produce a final verdict."
    )

    try:
        user_idea = input("\nYour idea:\n> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nInput cancelled.")
        return

    if not user_idea:
        print("\nError: Your idea cannot be empty.")
        return

    print("\nStarting evaluation...")
    print(
        "The Builder, Architect, Skeptic, and Verdict agents "
        "will process your idea."
    )
    print("This may take a while...")

    try:
        result = run_workflow(user_idea)
        display_report(result)

    except WorkflowError as exc:
        print(f"\nEvaluation failed: {exc}")

        if exc.__cause__ is not None:
            print(
                f"Underlying error: "
                f"{type(exc.__cause__).__name__}: {exc.__cause__}"
            )

    except KeyboardInterrupt:
        print("\nEvaluation interrupted by the user.")


if __name__ == "__main__":
    main()
