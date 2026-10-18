import json
from json import JSONDecodeError

from pydantic import ValidationError

from parallax.config import get_settings
from parallax.llm.client import get_llm_client
from parallax.schemas.assessment import AgentAssessment, AgentRole
from parallax.schemas.proposal import Proposal


class SkepticAgentError(Exception):
    """Raised when the Skeptic agen cannot produce a valid assessment."""


def challenge_proposal(proposal: Proposal) -> AgentAssessment:
    """Critically evaluate a proposal and identify its weaknesses"""

    settings = get_settings()
    client = get_llm_client()

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": """
                You are the Skeptic Agent in Parallax, a multi-agent
                proposal evaluation system.

                Your responsibility is to critically challenge the
                supplied proposal. Do not simply repeat a technical
                feasibility assessment.

                Investigate:
                - Unsupported assumptions and unverified claims
                - Missing requirements and overlooked edge cases
                - Unrealistic success criteria or timelines
                - Hidden costs, dependencies, and operational risks
                - Privacy, security, reliability, and usability concerns
                - Whether the proposed solution is unnecessarily complex
                - Conditions under which the proposal might fail

                Be rigorous, fair, and evidence-based. Do not reject an
                idea merely to appear critical. Acknowledge genuine
                strengths when relevant, but prioritize meaningful
                weaknesses and concrete risks.

                Distinguish explicit facts from assumptions and inferences.
                Never invent evidence or present speculation as established fact.

                Return ONLY one valid JSON object. Do not use Markdown
                fences or add commentary.

                Follow this exact structure:

                {
                    "agent": "skeptic",
                    "summary": "A concise critical assessment of the proposal.",
                    "findings": [
                        {
                            "title": "A specific concern",
                            "explanation": "Explain the concern and its potential impact.",
                            "severity": "medium",
                            "evidence": [
                                "A specific fact from the supplied proposal."
                            ]
                        }
                    ],
                    "assumptions": [
                        "An assumption that requires verification."
                    ],
                    "recommendations": [
                        "A concrete action to address a concern."
                    ]
                }

                STRICT REQUIREMENTS:
                - The agent field must be exactly "skeptic".
                - Every finding must contain title, explanation, severity, and evidence.
                - Every evidence field must be an array of strings, never a single string.
                - Severity must be low, medium, high, or critical.
                - Findings must contain between 1 and 20 items.
                - Recommendations must contain between 1 and 10 items.
                - Assumptions may be an empty array.
                - Do not add fields outside the required schema.
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
        raise SkepticAgentError("The model returned an empty assessment.")

    try:
        payload = json.loads(content)
    except JSONDecodeError as exc:
        raise SkepticAgentError("The model returned malformed JSON") from exc

    try:
        assessment = AgentAssessment.model_validate(payload)
    except ValidationError as exc:
        raise SkepticAgentError(
            "The model returned a assessment that failed validation"
        ) from exc

    if assessment.agent != AgentRole.SKEPTIC:
        raise SkepticAgentError(
            "The model returned an assesment for the wrong agent role."
        )

    return assessment
