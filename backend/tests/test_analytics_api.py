from unittest.mock import Mock

from fastapi.testclient import TestClient

from src.api import arbitration_history
from src.api.main import app
from src.api.schemas.responses import EvaluationResponse
from src.api.routes import analytics
from tests.test_evaluate_api import graph_result


def test_analytics_endpoint_returns_persisted_metrics(monkeypatch, tmp_path):
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(tmp_path / "arbitrations.sqlite3"))
    arbitration_id = arbitration_history.create("Question?")
    arbitration_history.complete(
        arbitration_id, EvaluationResponse.model_validate(graph_result())
    )

    with TestClient(app) as client:
        response = client.get("/v1/analytics")

    assert response.status_code == 200
    assert response.json() == {
        "arbitrations": {"total": 1, "assessed": 1, "inconclusive": 0},
        "critics": {
            "accuracy": {"evaluations": 1, "average_score": 2.0, "issues": 1},
            "logic": {"evaluations": 0, "average_score": 0.0, "issues": 0},
            "completeness": {"evaluations": 0, "average_score": 0.0, "issues": 0},
        },
        "adjudication": {"requested": 1, "confirmed_issues": 1, "dismissed_issues": 0},
    }
    assert len(arbitration_history.list_analytics_records()) == 1


def test_analytics_endpoint_returns_zero_values_for_empty_database(monkeypatch, tmp_path):
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(tmp_path / "arbitrations.sqlite3"))

    with TestClient(app) as client:
        response = client.get("/v1/analytics")

    assert response.status_code == 200
    assert response.json() == {
        "arbitrations": {"total": 0, "assessed": 0, "inconclusive": 0},
        "critics": {
            dimension: {"evaluations": 0, "average_score": 0.0, "issues": 0}
            for dimension in ("accuracy", "logic", "completeness")
        },
        "adjudication": {"requested": 0, "confirmed_issues": 0, "dismissed_issues": 0},
    }


def test_analytics_endpoint_hides_storage_error(monkeypatch, tmp_path):
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(tmp_path / "arbitrations.sqlite3"))
    monkeypatch.setattr(
        analytics, "get_analytics", Mock(side_effect=RuntimeError("private database detail"))
    )

    with TestClient(app) as client:
        response = client.get("/v1/analytics")

    assert response.status_code == 500
    assert response.json() == {"detail": "Analytics retrieval failed"}
    assert "private database detail" not in response.text
