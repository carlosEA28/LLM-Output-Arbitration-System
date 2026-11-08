"""Find substantive contradictions between the critics' reported issues."""

from itertools import combinations

from langchain.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.arbitration.schemas.disagreement import ConflictAssessment
from src.arbitration.states import ArbitrationState
from src.prompts.disagreements import DisagreementPrompts



from src.arbitration.states import ArbitrationState


def detect_disagreements(state: ArbitrationState) -> dict:
    critiques = state.get("critiques", [])
    disagreements = []

    with_issues = [
        critique.dimension.value
        for critique in critiques
        if critique.issues
    ]

    without_issues = [
        critique.dimension.value
        for critique in critiques
        if not critique.issues
    ]

    if with_issues and without_issues:
        disagreements.append(
            f"Issues detected by {', '.join(with_issues)}, "
            f"but not by {', '.join(without_issues)}."
        )

    return {
        "disagreements": disagreements,
        "requires_adjudication": bool(disagreements),
    }
