
from enum import Enum

from pydantic import BaseModel, Field


class DimensionsEnum(str, Enum):
    accuracy = "accuracy"
    logic = "logic"
    completeness = "completeness"


class SeverityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class IssueSchema(BaseModel):
    quote: str | None = Field(
        default=None,
        description="Exact excerpt from the evaluated response related to the issue."
    )

    description: str = Field(
        min_length=1,
        description="Explanation of the identified issue."
    )

    severity: SeverityEnum = Field(
        description="Severity level of the identified issue."
    )


class CritiqueSchema(BaseModel):
    dimension: DimensionsEnum = Field(
        description="Evaluation dimension assigned to the critic."
    )

    score: int = Field(
        ge=1,
        le=5,
        description="Quality score for the evaluated dimension, from 1 to 5."
    )

    issues: list[IssueSchema] = Field(
        default_factory=list,
        description="List of issues identified during the evaluation."
    )

    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Critic's self-reported confidence in its evaluation."
    )
