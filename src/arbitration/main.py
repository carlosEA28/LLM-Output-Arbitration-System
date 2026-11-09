
from src.arbitration.graph import run_agents_graph


from src.nodes.adjudicator import adjudicator
from src.arbitration.schemas.critique import (
    CritiqueSchema,
    IssueSchema,
    DimensionsEnum,
    SeverityEnum,
)


def test_adjudicator():
    state = {
        "original_question": "What is the capital of France?",
        "generated_output": "The capital of France is Berlin.",
        "critiques": [
            CritiqueSchema(
                dimension=DimensionsEnum.accuracy,
                score=5,
                issues=[
                    IssueSchema(
                        quote="The capital of France is Berlin.",
                        description="The capital of France is Paris.",
                        severity=SeverityEnum.high,
                    )
                ],
                confidence=0.9,
            )
        ],
        "disagreements": [
            "accuracy: High score despite identified issues."
        ],
        "requires_adjudication": True,
        "failed_critics": [],
    }

    result = adjudicator(state)

    print("\n=== ADJUDICATOR TEST ===")
    print(result["adjudication"])



def main():
    graph = run_agents_graph()

    initial_state = {
        "original_question": "What is the capital of France?",
        "generated_output": "The capital of France is Paris.",
        "critiques": [],
        "failed_critics": [],
    }

    result = graph.invoke(initial_state)

    print("\n=== CRITICS ===")
    for critique in result["critiques"]:
        print(f"{critique.dimension.value}: {critique.score}/5")
        print(f"Issues: {critique.issues}")

    print("\n=== COLLECTION ===")
    print(f"Complete: {result.get('critiques_complete')}")
    print(f"Failed critics: {result.get('failed_critics', [])}")

    print("\n=== DISAGREEMENTS ===")
    print(f"Disagreements: {result.get('disagreements', [])}")
    print(f"Requires adjudication: {result.get('requires_adjudication')}")

    print("\n=== ADJUDICATION ===")
    print(result.get("adjudication"))

    print("\n=== VERDICT ===")
    verdict = result.get("verdict")

    if verdict:
        print(verdict.model_dump_json(indent=2))
    else:
        print("No verdict generated")


if __name__ == "__main__":
    test_adjudicator()
