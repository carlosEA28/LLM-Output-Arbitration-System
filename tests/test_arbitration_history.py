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
