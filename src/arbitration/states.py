
import operator
from typing import Annotated, TypedDict

from src.arbitration.schemas.critique import CritiqueSchema


class ArbitrationState(TypedDict):
    original_question: str
    generated_output: str

    critiques: Annotated[list[CritiqueSchema], operator.add]

    disagreements: list[str]
    requires_adjudication: bool
    verdict: str | None
    failed_critics: list[str]
