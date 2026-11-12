from datetime import datetime, timezone
from uuid import UUID

from src.api import arbitration_history
from tests.test_evaluate_api import graph_result
from src.api.schemas.responses import EvaluationResponse


def test_history_persists_across_connections_with_optional_fields(monkeypatch, tmp_path):
    database = tmp_path / "arbitrations.sqlite3"
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(database))

    arbitration_id = arbitration_history.create("Question?")
    pending = arbitration_history.get(arbitration_id)
    assert UUID(pending["id"]) == arbitration_id
    assert datetime.fromisoformat(pending["created_at"]).tzinfo == timezone.utc
    assert pending["status"] == "pending"
    assert pending["generated_output"] is None
    assert pending["evaluation"] is None

    arbitration_history.save_generated_output(arbitration_id, "Answer.")
    evaluation = EvaluationResponse.model_validate(graph_result())
    arbitration_history.complete(arbitration_id, evaluation)

    stored = arbitration_history.get(arbitration_id)
    assert stored["status"] == "completed"
    assert stored["generated_output"] == "Answer."
    assert stored["evaluation"] == evaluation.model_dump(mode="json")
    assert arbitration_history.get(UUID("00000000-0000-0000-0000-000000000000")) is None


def test_analytics_records_read_all_statuses_without_changing_history(monkeypatch, tmp_path):
    database = tmp_path / "arbitrations.sqlite3"
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(database))

    pending_id = arbitration_history.create("Pending?")
    completed_id = arbitration_history.create("Completed?")
    failed_id = arbitration_history.create("Failed?")
    arbitration_history.complete(
        completed_id, EvaluationResponse.model_validate(graph_result())
    )
    arbitration_history.fail(failed_id, timed_out=False)

    records = arbitration_history.list_analytics_records()

    assert len(records) == 3
    assert sorted(status for status, _ in records) == ["completed", "failed", "pending"]
    assert sum(evaluation_json is not None for _, evaluation_json in records) == 1
    assert arbitration_history.get(pending_id)["status"] == "pending"
    assert arbitration_history.get(completed_id)["status"] == "completed"
    assert arbitration_history.get(failed_id)["status"] == "failed"
