
from pydantic import BaseModel, ConfigDict, Field, field_validator

class Proposal(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
    )

    title: str = Field(
        min_length=3,
        max_length=150,
        description="A concise title for the proposal",
    )

    description: str = Field(
        min_length=20,
        max_length=10_000,
        description="A detailed description of the proposed idea.",
    )

    objective: str = Field(
        min_length=10,
        max_length=2_000,
        description="The main outcome of the proposed aims to achieve.",
    )

    constraints: list[str] = Field(
        default_factory=list,
        max_length=20,
        description="Budget, timeline, technical, or other constraints.",
    )

    success_criteria: list[str] = Field(
        min_length=1,
        max_length=10,
        description="Measurable or observable critaria for success.",
    )

    @field_validator("title", "description", "objective")
    @classmethod
    def reject_blank_text(cls, value: str) -> str:
        if not value:
            raise ValueError("This field cannot be empty")
        return value

    @field_validator("constraints", "success_criteria")
    @classmethod
    def reject_blank_list_items(cls, values: list[str]) -> list[str]:
        if any(not item for item in values):
            raise ValueError("List items cannot be blank.")
        return values
        
        
