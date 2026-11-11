
"""Detect inconsistencies in critic evaluations."""

from src.arbitration.states import ArbitrationState


def detect_disagreements(state: ArbitrationState) -> dict:
    critiques = state.get("critiques", [])
    disagreements = []

    for critique in critiques:
        dimension = critique.dimension.value

        if critique.score <= 2 and not critique.issues:
            disagreements.append(
                f"{dimension}: Low score without identified issues."
            )

        if critique.score == 5 and critique.issues:
            disagreements.append(
                f"{dimension}: High score despite identified issues."
            )

    return {
        "disagreements": disagreements,
        "requires_adjudication": bool(disagreements),
    }
