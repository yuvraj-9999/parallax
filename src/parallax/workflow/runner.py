from parallax.schemas.verdict import Verdict
from parallax.workflow.graph import build_graph


class WorkflowError(Exception):
    """Raised when the Parallax workflow cannon complete successfully"""

def run_workflow(user_idea: str) -> dict:
    """Excecute the Parallax workflow for the user's idea."""

    if not user_idea or not user_idea.strip():
        raise ValueError("The user's idea cannot be empty.")

    graph = build_graph()

    try:
        result = graph.invoke(
            {
                "user_idea": user_idea,
                "proposal": None,
                "architect_assessment": None,
                "skeptic_assessment": None,
                "verdict": None,
                "error": None,
            }
        )
    except Exception as exc:
        raise WorkflowError("Parallax could not complete the evaluation workflow") from exc

    verdict = result.get("verdict")

    if not isinstance(verdict, Verdict):
        raise WorkflowError("The workflow completed without producing a valid verdict.")


    return result    
    