import json
from json import JSONDecodeError

from pydantic import ValidationError

from parallax.config import get_settings
from parallax.llm.client import get_llm_client
from parallax.schemas.proposal import Proposal


class BuilderAgentError(Exception):
    """Raised when the Builder Agent cannot produce a valid proposal"""


def build_proposal(user_idea: str) -> Proposal:
    """Generate and validate a structured proposal from user's idea"""

    user_idea = user_idea.strip()

    if not user_idea:
        raise ValueError("The users idea cannot be empty")

    settings = get_settings()
    client = get_llm_client()

    response = client.chat.completions.create(
        model=settings.openrouter_model,
        temperature=0.2,
        messages=[
            {
                "role": "system",
                "content": """
                            You are the Builder Agent in Parallax, a multi-agent
                            proposal evaluation system.

                            Your responsibility is to transform the user's idea into
                            a clear, practical, structured proposal.

                            The proposal must contain:
                            - title
                            - description
                            - objective
                            - constraints
                            - success_criteria

                            Return ONLY a valid JSON object matching the required
                            schema. Do not use Markdown fences or add commentary.

                            Be realistic. Do not invent facts about the user's
                            resources, budget, or circumstances. If information is
                            missing, state reasonable assumptions explicitly in the
                            description or identify the uncertainty in the constraints.
                            """.strip(),
            },
            {
                "role": "user",
                "content": user_idea,
            },
        ],
    )

    content = response.choices[0].message.content

    if not content or not content.strip():
        raise BuilderAgentError("The model returned an empty response")

    try:
        payload = json.loads(content)
    except JSONDecodeError as exc:
        raise BuilderAgentError("The model returned malformed JSON.") from exc

    try:
        return Proposal.model_validate(payload)
    except ValidationError as exc:
        raise BuilderAgentError(
            "The model returned a proposal that failed validation."
        ) from exc
