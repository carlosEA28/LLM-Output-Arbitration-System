
from typing import Literal

from pydantic import BaseModel, Field

from src.arbitration.schemas.critique import IssueSchema


class DismissedIssueSchema(BaseModel):
    issue: IssueSchema
    reason: str = Field(
        min_length=1,
        description="Reason for dismissing the issue."
    )


class AdjudicationSchema(BaseModel):
    confirmed_issues: list[IssueSchema] = Field(default_factory=list)
    dismissed_issues: list[DismissedIssueSchema] = Field(default_factory=list)


class VerdictSchema(BaseModel):
    overall_score: int = Field(ge=1, le=10)
    confidence: float = Field(ge=0.0, le=1.0)

    confirmed_issues: list[IssueSchema] = Field(default_factory=list)
    dismissed_issues: list[DismissedIssueSchema] = Field(default_factory=list)
    unverified_issues: list[IssueSchema] = Field(default_factory=list)

    summary: str = Field(min_length=1)
    status: Literal["assessed", "inconclusive"] = "assessed"
