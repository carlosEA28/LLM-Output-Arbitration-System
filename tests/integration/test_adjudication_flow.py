
from src.arbitration.schemas.critique import (
    CritiqueSchema,
    DimensionsEnum,
    IssueSchema,
    SeverityEnum,
)


def test_full_adjudication_flow(monkeypatch):
    from src.arbitration import graph as graph_module

    issue = IssueSchema(
        quote="The capital of France is Berlin.",
        description="The capital of France is Paris, not Berlin.",
        severity=SeverityEnum.critical,
    )

    def fake_accuracy(state):
        return {
            "critiques": [
                CritiqueSchema(
                    dimension=DimensionsEnum.accuracy,
                    score=5,
                    issues=[issue],
                    confidence=0.9,
                )
            ]
        }

    def fake_logic(state):
        return {
            "critiques": [
                CritiqueSchema(
                    dimension=DimensionsEnum.logic,
                    score=5,
                    issues=[],
                    confidence=0.9,
                )
            ]
        }

    def fake_completeness(state):
        return {
            "critiques": [
                CritiqueSchema(
                    dimension=DimensionsEnum.completeness,
                    score=5,
                    issues=[],
                    confidence=0.9,
                )
            ]
        }

    monkeypatch.setattr(
        graph_module, "accuracy_critic", fake_accuracy
    )
    monkeypatch.setattr(
        graph_module, "logic_critic", fake_logic
    )
    monkeypatch.setattr(
        graph_module, "completeness_critic", fake_completeness
    )

    graph = graph_module.run_agents_graph()

    result = graph.invoke({
        "original_question": "What is the capital of France?",
        "generated_output": "The capital of France is Berlin.",
        "critiques": [],
        "failed_critics": [],
    })

    assert result["critiques_complete"] is True
    assert result["requires_adjudication"] is True
    assert result["adjudication"] is not None

    verdict = result["verdict"]

    assert verdict is not None
    assert issue in verdict.confirmed_issues
    assert issue not in verdict.unverified_issues
    assert verdict.overall_score <= 4
    assert verdict.status == "assessed"

    print("\nPASS: Full adjudication flow")
