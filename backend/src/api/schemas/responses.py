from datetime import datetime
from typing import Literal
from uuid import UUID

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


class BatchEvaluationItemResponse(BaseModel):
    index: int
    status: Literal["completed", "failed", "timed_out"]
    evaluation: EvaluationResponse | None
    error: str | None


class BatchEvaluationResponse(BaseModel):
    results: list[BatchEvaluationItemResponse]


class GenerationEvaluationResponse(EvaluationResponse):
    id: UUID
    generated_output: str


class ArbitrationHistoryResponse(BaseModel):
    id: UUID
    status: Literal["pending", "completed", "failed", "timed_out"]
    created_at: datetime
    original_question: str
    generated_output: str | None
    evaluation: EvaluationResponse | None


class ArbitrationMetricsResponse(BaseModel):
    total: int
    assessed: int
    inconclusive: int


class CriticMetricsResponse(BaseModel):
    evaluations: int
    average_score: float
    issues: int


class CriticsMetricsResponse(BaseModel):
    accuracy: CriticMetricsResponse
    logic: CriticMetricsResponse
    completeness: CriticMetricsResponse


class AdjudicationMetricsResponse(BaseModel):
    requested: int
    confirmed_issues: int
    dismissed_issues: int


class AnalyticsResponse(BaseModel):
    arbitrations: ArbitrationMetricsResponse
    critics: CriticsMetricsResponse
    adjudication: AdjudicationMetricsResponse
