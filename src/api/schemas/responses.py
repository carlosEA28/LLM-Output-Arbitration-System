from pydantic import BaseModel

from src.arbitration.schemas.critique import CritiqueSchema
from src.arbitration.schemas.verdict import AdjudicationSchema, VerdictSchema


class EvaluationResponse(BaseModel):
    critiques: list[CritiqueSchema]
    failed_critics: list[str]
    missing_dimensions: list[str]
    duplicate_dimensions: list[str]
    critiques_complete: bool
    disagreements: list[str]
    requires_adjudication: bool
    adjudication: AdjudicationSchema | None
    verdict: VerdictSchema


class GenerationEvaluationResponse(EvaluationResponse):
    generated_output: str
