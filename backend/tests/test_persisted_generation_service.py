from unittest.mock import Mock

import pytest

from src.api import arbitration_history
from src.api.services import arbitration_service
from src.arbitration.schemas.verdict import VerdictSchema
from tests.test_evaluate_api import graph_result


@pytest.fixture(autouse=True)
def database_path(monkeypatch, tmp_path):
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(tmp_path / "arbitrations.sqlite3"))


@pytest.mark.parametrize("inconclusive", [False, True])
def test_persisted_service_completes_existing_graph_result(monkeypatch, inconclusive):
    observed = []

    def generate(question):
        assert question == "Question?"
        return " Generated answer. "

    def invoke(state):
        assert state["original_question"] == "Question?"
        assert state["generated_output"] == " Generated answer. "
        assert state["critiques"] == []
        assert state["failed_critics"] == []
        return graph_result(
            verdict=VerdictSchema(
                overall_score=1, confidence=0.5, summary="Partial", status="inconclusive"
            )
        ) if inconclusive else graph_result()

    graph = Mock()
    graph.invoke.side_effect = invoke
    monkeypatch.setattr(arbitration_service, "generate_response", generate)
    monkeypatch.setattr(arbitration_service, "run_agents_graph", Mock(return_value=graph))
    original_save = arbitration_history.save_generated_output

    def save_output(arbitration_id, output):
        assert arbitration_history.get(arbitration_id)["status"] == "pending"
        observed.append(output)
        original_save(arbitration_id, output)

    monkeypatch.setattr(arbitration_history, "save_generated_output", save_output)
    response = arbitration_service.generate_and_evaluate_persisted("Question?")

    stored = arbitration_history.get(response.id)
    assert observed == [" Generated answer. "]
    assert stored["status"] == "completed"
    assert stored["original_question"] == "Question?"
    assert stored["generated_output"] == " Generated answer. "
    assert stored["evaluation"]["verdict"] == response.verdict.model_dump(mode="json")
    assert stored["evaluation"]["critiques"] == [
        critique.model_dump(mode="json") for critique in response.critiques
    ]


@pytest.mark.parametrize(
    ("failure_stage", "error", "expected_status"),
    [
        ("generation", RuntimeError("provider-token-sensitive-payload"), "failed"),
        ("generation", TimeoutError("provider-token-sensitive-payload"), "timed_out"),
        ("generation", " \t ", "failed"),
        ("evaluation", RuntimeError("provider-token-sensitive-payload"), "failed"),
        ("evaluation", TimeoutError("provider-token-sensitive-payload"), "timed_out"),
        ("evaluation", {"verdict": None}, "failed"),
    ],
)
def test_persisted_service_records_safe_failures(
    monkeypatch, failure_stage, error, expected_status
):
    if failure_stage == "generation":
        generator = Mock(side_effect=error) if isinstance(error, Exception) else Mock(return_value=error)
        evaluator = Mock()
    else:
        generator = Mock(return_value="Generated answer.")
        evaluator = Mock(side_effect=error) if isinstance(error, Exception) else Mock(return_value=error)
    monkeypatch.setattr(arbitration_service, "generate_response", generator)
    monkeypatch.setattr(arbitration_service, "evaluate_response", evaluator)

    with pytest.raises(arbitration_service.PersistedExecutionError) as caught:
        arbitration_service.generate_and_evaluate_persisted("Question?")

    stored = arbitration_history.get(caught.value.arbitration_id)
    assert stored["status"] == expected_status
    assert stored["original_question"] == "Question?"
    assert stored["generated_output"] == (
        None if failure_stage == "generation" else "Generated answer."
    )
    assert stored["evaluation"] is None
    assert "provider-token-sensitive-payload" not in str(stored)
    assert "provider-token-sensitive-payload" not in str(caught.value)
    if failure_stage == "generation":
        evaluator.assert_not_called()
