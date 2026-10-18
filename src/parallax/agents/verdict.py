import json
from json import JSONDecodeError

from pydantic import ValidationError

from parallax.config import get_settings
from parallax.llm.client import get_llm_client
from parallax.schemas.assessment import AgentAssessment, AgentRole
from parallax.schemas.proposal import Proposal
from parallax.schemas.verdict import Verdict


class VerdictAgentError(Exception):
    """Raised when the Verdict Agent cannot produce a valid verdict"""


def evaluate_proposal(
    proposal: Proposal,
    architect_assessment: AgentAssessment,
    skeptic_assessment: AgentAssessment,
) -> Verdict:
    """Synthesize two independent assessments into a final verdict."""

    if architect_assessment.agent != AgentRole.ARCHITECT:
        raise ValueError("architect_assessment must belong to the Architect Agent.")

    if skeptic_assessment.agent != AgentRole.SKEPTIC:
        raise ValueError("skeptic_assessment must belong to the skeptic Agent")

    settings = get_settings()
    client = get_llm_client()

    input_data = {
        "proposal": proposal.model_dump(mode="json"),
        "architect_assessment": architect_assessment.model_dump(mode="json"),
        "skeptic_assessment": skeptic_assessment.model_dump(mode="json"),
    }

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        temperature=0.2,
        max_tokens=2500,
        messages=[
            {
                "role": "system",
                "content": """
                            You are the Verdict Agent in Parallax, a multi-agent
                            proposal evaluation system.

                            You receive a proposal and two independent assessments:
                            one from the Architect and one from the Skeptic.

                            Your responsibility is to synthesize their evidence and
                            produce a balanced, defensible final decision.

                            Choose exactly one decision:
                            - proceed: the proposal is sufficiently sound to move forward.
                            - revise: the proposal has potential but needs specific changes.
                            - reject: fundamental problems make the proposal unsuitable
                              in its current form.

                            Decision-making requirements:
                            - Evaluate the actual evidence, not merely the number of findings.
                            - Consider severity, likelihood, impact, and whether risks can
                              reasonably be mitigated.
                            - Distinguish critical blockers from manageable trade-offs.
                            - Do not automatically reject a proposal because the Skeptic
                              identified several concerns.
                            - Do not automatically approve a proposal because the Architect
                              considers it technically feasible.
                            - Do not invent facts or claim that an assessment proves something
                              it does not establish.
                            - Explain the reasoning behind the selected decision.
                            - Provide concrete, prioritized actions where appropriate.
                            - Key strengths and key concerns may be empty arrays.
                            - Recommendations must contain at least one actionable item.

                            Return ONLY one valid JSON object matching this structure:

                            {
                                "decision": "revise",
                                "rationale": "Explain why this decision is justified.",
                                "key_strengths": [
                                    "A meaningful strength supported by the input."
                                ],
                                "key_concerns": [
                                    "A significant unresolved concern supported by the input."
                                ],
                                "recommendations": [
                                    "A concrete action that should be taken next."
                                ]
                            }

                            STRICT REQUIREMENTS:
                            - decision must be exactly "proceed", "revise", or "reject".
                            - rationale must explain the decision and be sufficiently detailed.
                            - key_strengths and key_concerns must be arrays of strings.
                            - recommendations must be an array of strings.
                            - Do not add fields outside the required schema.
                            - Return JSON only, without Markdown fences or commentary.
                            """.strip(),
            },
            {
                "role": "user",
                "content": json.dumps(input_data, indent=2),
            },
        ],
    )

    if response.choices[0].finish_reason == "length":
        raise VerdictAgentError(
            "The model response was truncated because it reached "
            "the output token limit."
        )

    content = response.choices[0].message.content

    if not content or not content.strip():
        raise VerdictAgentError("The model returned an empty verdict")

    try:
        payload = json.loads(content)
    except JSONDecodeError as exc:
        raise VerdictAgentError("The model returned malformed JSON.") from exc

    try:
        return Verdict.model_validate(payload)
    except ValidationError as exc:
        raise VerdictAgentError(
            "The model returned a verdict that failed validation."
        ) from exc
