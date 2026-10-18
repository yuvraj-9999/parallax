from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AgentRole(str, Enum):
    BUILDER = "builder"
    ARCHITECT = "architect"
    SKEPTIC = "skeptic"


class Severity(str, Enum):
    LOW = ("low",)
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    title: str = Field(min_length=3, max_length=150)
    explanation: str = Field(min_length=10, max_length=2_000)
    severity: Severity
    evidence: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("evidence")
    @classmethod
    def validate_evidence(cls, values: list[str]) -> list[str]:
        if any(not value for value in values):
            raise ValueError("Evidence items cannot be blank.")
        return values


class AgentAssessment(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    agent: AgentRole
    summary: str = Field(min_length=10, max_length=2_000)
    findings: list[Finding] = Field(min_length=1, max_length=20)
    assumptions: list[str] = Field(default_factory=list, max_length=10)
    recommendations: list[str] = Field(min_length=1, max_length=10)

    @field_validator("assumptions", "recommendations")
    @classmethod
    def validate_text_items(cls, values: list[str]) -> list[str]:
        if any(not value for value in values):
            raise ValueError("List items cannot be blank.")
        return values
