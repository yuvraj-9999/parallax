from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class VerdictDecision(str, Enum):
    PROCEED = ("proceed",)
    REVISE = ("revise",)
    REJECT = ("reject",)


class Verdict(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    decision: VerdictDecision = Field(description="The final decision on the proposal")

    rationale: str = Field(
        min_length=20,
        max_length=4_000,
        description="The reasoning supporting the final decision.",
    )

    key_strengths: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="The strongest aspects of the proposal.",
    )

    key_concerns: list[str] = Field(
        default_factory=list,
        max_length=10,
        description="the most important unresolved concerns.",
    )

    recommendations: list[str] = Field(
        min_length=1,
        max_length=10,
        description="Concrete actions based on the verdict.",
    )

    @field_validator("key_strengths", "key_concerns", "recommendations")
    @classmethod
    def validate_text_items(cls, values: list[str]) -> list[str]:
        if any(not value for value in values):
            raise ValueError("List items cannot be blank.")
        return values
