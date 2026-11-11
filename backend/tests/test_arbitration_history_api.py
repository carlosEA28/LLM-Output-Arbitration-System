from datetime import datetime, timezone
from unittest.mock import Mock
from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes import arbitration
from src.api.services import arbitration_service
from src.arbitration.schemas.verdict import VerdictSchema
from tests.test_evaluate_api import graph_result


@pytest.fixture
def database_path(monkeypatch, tmp_path):
    path = tmp_path / "arbitrations.sqlite3"
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(path))
    return path


def test_successful_generation_is_retrievable_from_another_client(monkeypatch, database_path):
    monkeypatch.setattr(
        arbitration_service, "generate_response", Mock(return_value="Generated answer.")
    )
    monkeypatch.setattr(arbitration_service, "evaluate_response", Mock(return_value=graph_result()))

    with TestClient(app) as client:
        created = client.post("/generate-and-evaluate", json={"original_question": "Question?"})

    assert created.status_code == 200
    arbitration_id = created.json()["id"]
    UUID(arbitration_id)
    assert created.headers["X-Arbitration-ID"] == arbitration_id
    assert database_path.exists()

    with TestClient(app) as client:
        retrieved = client.get(f"/v1/arbitrations/{arbitration_id}")

    assert retrieved.status_code == 200
    record = retrieved.json()
    assert record["id"] == arbitration_id
    assert record["status"] == "completed"
    assert datetime.fromisoformat(record["created_at"]).tzinfo == timezone.utc
    assert record["original_question"] == "Question?"
    assert record["generated_output"] == "Generated answer."
    assert record["evaluation"] == {
        key: value for key, value in created.json().items()
        if key not in {"id", "generated_output"}
    }


def test_inconclusive_verdict_is_still_completed(monkeypatch, database_path):
    verdict = VerdictSchema(
        overall_score=1, confidence=0.5, summary="Partial", status="inconclusive"
    )
    monkeypatch.setattr(
        arbitration_service, "generate_response", Mock(return_value="Generated answer.")
    )
    monkeypatch.setattr(
        arbitration_service, "evaluate_response",
        Mock(return_value=graph_result(verdict=verdict, failed_critics=["logic_critic"])),
    )

    with TestClient(app) as client:
        created = client.post("/generate-and-evaluate", json={"original_question": "Question?"})
        retrieved = client.get(f"/v1/arbitrations/{created.json()['id']}")

    assert created.status_code == 200
    assert retrieved.json()["status"] == "completed"
    assert retrieved.json()["evaluation"]["verdict"]["status"] == "inconclusive"
    assert retrieved.json()["evaluation"]["failed_critics"] == ["logic_critic"]


@pytest.mark.parametrize(
    ("stage", "error", "expected_http", "expected_status"),
    [
        ("generation", RuntimeError("private-provider-payload"), 500, "failed"),
        ("generation", TimeoutError("private-provider-payload"), 504, "timed_out"),
        ("evaluation", RuntimeError("private-provider-payload"), 500, "failed"),
        ("evaluation", TimeoutError("private-provider-payload"), 504, "timed_out"),
    ],
)
def test_failed_generation_has_safe_retrievable_record(
    monkeypatch, database_path, stage, error, expected_http, expected_status
):
    generator = Mock(return_value="Generated answer.")
    evaluator = Mock(return_value=graph_result())
    if stage == "generation":
        generator.side_effect = error
    else:
        evaluator.side_effect = error
    monkeypatch.setattr(arbitration_service, "generate_response", generator)
    monkeypatch.setattr(arbitration_service, "evaluate_response", evaluator)

    with TestClient(app) as client:
        created = client.post("/generate-and-evaluate", json={"original_question": "Question?"})
        arbitration_id = created.headers["X-Arbitration-ID"]
        retrieved = client.get(f"/v1/arbitrations/{arbitration_id}")

    assert created.status_code == expected_http
    assert created.json() == {
        "detail": (
            "Generation and evaluation timed out"
            if expected_http == 504 else "Generation and evaluation failed"
        )
    }
    assert retrieved.status_code == 200
    assert retrieved.json()["status"] == expected_status
    assert retrieved.json()["generated_output"] == (
        None if stage == "generation" else "Generated answer."
    )
    assert retrieved.json()["evaluation"] is None
    assert "private-provider-payload" not in created.text
    assert "private-provider-payload" not in retrieved.text


def test_unknown_and_malformed_ids(monkeypatch, database_path):
    with TestClient(app) as client:
        unknown = client.get(f"/v1/arbitrations/{uuid4()}")
        malformed = client.get("/v1/arbitrations/not-a-uuid")

    assert unknown.status_code == 404
    assert malformed.status_code == 422
    assert malformed.json() == {"detail": "Invalid request"}


def test_invalid_generation_and_direct_evaluation_do_not_create_history(
    monkeypatch, database_path
):
    monkeypatch.setattr(arbitration, "evaluate_response", Mock(return_value=graph_result()))
    with TestClient(app) as client:
        invalid = client.post("/generate-and-evaluate", json={"original_question": " "})
        direct = client.post(
            "/evaluate",
            json={"original_question": "Question?", "generated_output": "Answer."},
        )

    assert invalid.status_code == 422
    assert direct.status_code == 200
    assert not database_path.exists()
