"""Structured assessment of contradictions between critic issues."""

from pydantic import BaseModel, Field


class IssueConflict(BaseModel):
    first_issue: int = Field(description="Index of the first conflicting issue")
    second_issue: int = Field(description="Index of the second conflicting issue")
    explanation: str = Field(min_length=1, description="The specific incompatible claims")


class ConflictAssessment(BaseModel):
    conflicts: list[IssueConflict] = Field(default_factory=list)
