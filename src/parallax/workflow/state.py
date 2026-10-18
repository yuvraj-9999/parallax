from typing import TypedDict

from parallax.schemas.assessment import AgentAssessment
from parallax.schemas.proposal import Proposal
from parallax.schemas.verdict import Verdict


class ParallaxState(TypedDict):
    """Shared state passed between Parallax workflow nodes"""

    user_idea: str
    proposal: Proposal | None
    architect_assessment: AgentAssessment | None
    skeptic_assessment: AgentAssessment | None
    verdict: Verdict | None
    error: str | None