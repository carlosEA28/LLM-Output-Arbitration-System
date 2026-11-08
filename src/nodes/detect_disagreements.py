"""Find substantive contradictions between the critics' reported issues."""

from langchain.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from src.arbitration.schemas.disagreement import ConflictAssessment
from src.arbitration.states import ArbitrationState
from src.prompts.disagreements import DisagreementPrompts



from src.arbitration.states import ArbitrationState


def detect_disagreements(state: ArbitrationState) -> dict:
    critiques = state.get("critiques", [])

    if not critiques:
        return {
            "disagreements": [],
            "requires_adjudication": False,
        }

    disagreements = []

    for critique in critiques:
        if critique.score <= 2 and not critique.issues:
            disagreements.append(
                f"{critique.dimension.value}: "
                "Low score without identified issues."
            )

        if critique.score == 5 and critique.issues:
            disagreements.append(
                f"{critique.dimension.value}: "
                "High score despite identified issues."
            )

    return {
        "disagreements": disagreements,
        "requires_adjudication": bool(disagreements),
    }
