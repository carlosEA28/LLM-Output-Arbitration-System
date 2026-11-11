
import operator
from typing import Annotated, TypedDict

from src.arbitration.schemas.critique import CritiqueSchema
from src.arbitration.schemas.verdict import AdjudicationSchema, VerdictSchema


class ArbitrationState(TypedDict):
    # Input
    original_question: str
    generated_output: str

    # Critics
    critiques: Annotated[list[CritiqueSchema], operator.add]
    failed_critics: Annotated[list[str], operator.add]

    # Collection
    missing_dimensions: list[str]
    duplicate_dimensions: list[str]
    critiques_complete: bool

    # Disagreement detection
    disagreements: list[str]
    requires_adjudication: bool

    # Final evaluation
    adjudication: AdjudicationSchema | None
    verdict: VerdictSchema | None
