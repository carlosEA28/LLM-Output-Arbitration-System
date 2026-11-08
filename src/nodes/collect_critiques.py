from collections import Counter

from src.arbitration.schemas.critique import DimensionsEnum
from src.arbitration.states import ArbitrationState


def collect_critiques(state: ArbitrationState) -> dict:
    counts = Counter(critique.dimension.value for critique in state.get("critiques", []))
    missing_dimensions = [dimension.value for dimension in DimensionsEnum if counts[dimension.value] == 0]
    duplicate_dimensions = [dimension.value for dimension in DimensionsEnum if counts[dimension.value] > 1]
    failed_critics = state.get("failed_critics", [])

    return {
        "missing_dimensions": missing_dimensions,
        "duplicate_dimensions": duplicate_dimensions,
        "critiques_complete": not (missing_dimensions or duplicate_dimensions or failed_critics),
    }
