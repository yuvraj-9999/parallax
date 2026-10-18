import json
from json import JSONDecodeError

from pydantic import ValidationError

from parallax.config import get_settings
from parallax.llm.client import get_llm_client
from parallax.schemas.assessment import AgentAssessment, AgentRole
from parallax.schemas.proposal import Proposal


class ArchitectAgentError(Exception):
    """Raised when the architect agent cannot produce a valid assessment."""


def assess_proposal(proposal: Proposal) -> AgentAssessment:
    """Evaluate a proposal's technical feasibility and architecture."""

    settings = get_settings()
    client = get_llm_client()

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": """
                You are the Architect Agent in Parallax, a multi-agent
                proposal evaluation system.

                Evaluate the supplied proposal from a software engineering
                and technical architecture perspective.

                Assess:
                - Technical feasibility
                - Architectural suitability
                - Implementation complexity
                - Technical constraints and trade-offs
                - Important assumptions and risks
                - Concrete engineering recommendations

                Be analytical and evidence-based. Do not invent facts.
                Distinguish explicit proposal details from your assumptions.

                Return ONLY one valid JSON object. Do not use Markdown fences
                or add commentary.

                Follow this exact structure:

                {
                "agent": "architect",
                "summary": "A concise technical assessment of the proposal.",
                "findings": [
                    {
                        "title": "A specific technical finding",
                        "explanation": "Explain the issue and its technical impact.",
                        "severity": "medium",
                        "evidence": [
                            "First relevant fact from the proposal.",
                            "Second relevant fact from the proposal."
                        ]
                    }
                ],
                "assumptions": [
                    "An explicit assumption made during the assessment."
                ],
                "recommendations": [
                    "A concrete, actionable technical recommendation."
                ]
            }

                STRICT REQUIREMENTS:
                - Every finding's evidence MUST be an array of strings.
                - Never return evidence as a single string.
                - Each finding must contain title, explanation, severity, and evidence.
                - Severity must be exactly one of: low, medium, high, critical.
                - Agent must be exactly "architect".
                - Findings must contain between 1 and 20 items.
                - Recommendations must contain between 1 and 10 items.
                - Assumptions may be an empty array.
                - Do not invent evidence. Evidence must reference facts from the
                  supplied proposal. Put interpretations and inferences in explanations.
                - Do not add fields that are not in the schema.

                Severity must be one of: low, medium, high, critical.
                Each finding must have a meaningful title and explanation.
                Include actionable recommendations.
                Do not use Markdown fences or additional commentary.
                """.strip(),
            },
            {
                "role": "user",
                "content": proposal.model_dump_json(indent=2),
            },
        ],
    )

    content = response.choices[0].message.content

    if not content or not content.strip():
        raise ArchitectAgentError("The model returned an empty assessment.")

    try:
        payload = json.loads(content)
    except JSONDecodeError as exc:
        raise ArchitectAgentError("The model returned malformed JSON.") from exc

    try:
        assessment = AgentAssessment.model_validate(payload)
    except ValidationError as exc:
        raise ArchitectAgentError(
            "The model returned an assessment that failed validation."
        ) from exc

    if assessment.agent != AgentRole.ARCHITECT:
        raise ArchitectAgentError(
            "The model returned an assessment for the wrong agent role"
        )

    return assessment
