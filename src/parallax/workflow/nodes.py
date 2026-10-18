from parallax.agents.architect import assess_proposal
from parallax.agents.builder import build_proposal
from parallax.agents.skeptic import challenge_proposal
from parallax.agents.verdict import evaluate_proposal
from parallax.schemas.assessment import AgentAssessment
from parallax.schemas.proposal import Proposal
from parallax.workflow.state import ParallaxState


def builder_node(state: ParallaxState) -> dict:
    """Generate a validated proposal from the user's idea"""

    proposal = build_proposal(state["user_idea"])

    return {"proposal" : proposal}

def architect_node(state: ParallaxState) -> dict:
    """Assess the proposal's technical feasibility"""
    proposal: Proposal = state["proposal"]

    assessment: AgentAssessment = assess_proposal(proposal)

    return {"architect_assessment" : assessment}

def skeptic_node(state: ParallaxState) -> dict:
    """Challenge the proposal's assumptions and weknesses"""

    proposal: Proposal = state["proposal"]
    assessment: AgentAssessment = challenge_proposal(proposal)

    return {"skeptic_assessment" : assessment}

def verdict_node(state: ParallaxState) -> dict:
    """Synthesize the independent assessments into a verdict"""

    proposal: Proposal = state["proposal"]
    architect_assessment: AgentAssessment = state["architect_assessment"]
    skeptic_assessment: AgentAssessment = state["skeptic_assessment"]

    verdict = evaluate_proposal(proposal, architect_assessment, skeptic_assessment)

    return {"verdict": verdict}