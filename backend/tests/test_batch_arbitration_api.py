from unittest.mock import Mock, call

import httpx
import pytest
from fastapi.testclient import TestClient
from openai import APITimeoutError

from src.api.main import app
from src.api.routes import arbitration
from src.arbitration.schemas.verdict import VerdictSchema
from tests.test_evaluate_api import graph_result


ITEMS = [
    {"original_question": "First question?", "generated_output": "First answer."},
    {"original_question": "Second question?", "generated_output": "Second answer."},
]
URL = "/v1/arbitrate/batch"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"items": []},
        {"items": [ITEMS[0], {"original_question": "Second?"}]},
        {"items": [ITEMS[0], {"original_question": 3, "generated_output": "Answer."}]},
        {"items": [ITEMS[0], {"original_question": " ", "generated_output": "Answer."}]},
        {"items": [ITEMS[0], {"original_question": "Second?", "generated_output": "\t"}]},
    ],
)
def test_invalid_batch_rejects_all_items(monkeypatch, payload):
    service = Mock()
    monkeypatch.setattr(arbitration, "evaluate_response", service)

    with TestClient(app) as client:
        response = client.post(URL, json=payload)

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid request"}
    service.assert_not_called()


def test_batch_evaluates_pairs_in_order(monkeypatch):
    first = graph_result()
    second = graph_result(requires_adjudication=False)
    second.pop("adjudication")
    service = Mock(side_effect=[first, second])
    monkeypatch.setattr(arbitration, "evaluate_response", service)

    with TestClient(app) as client:
        response = client.post(URL, json={"items": ITEMS})

    assert response.status_code == 200
    assert service.call_args_list == [
        call("First question?", "First answer."),
        call("Second question?", "Second answer."),
    ]
    results = response.json()["results"]
    assert [(item["index"], item["status"]) for item in results] == [
        (0, "completed"), (1, "completed")
    ]
    assert results[0]["evaluation"]["verdict"] == first["verdict"].model_dump(mode="json")
    assert results[0]["evaluation"]["critiques"] == [
        first["critiques"][0].model_dump(mode="json")
    ]
    assert results[1]["evaluation"]["adjudication"] is None
    assert results[1]["evaluation"]["verdict"] == second["verdict"].model_dump(mode="json")
    assert all(item["error"] is None for item in results)


def test_batch_preserves_mixed_outcomes_and_continues(monkeypatch):
    secret = "token=private prompt=hidden provider traceback"
    third = {"original_question": "Third question?", "generated_output": "Third answer."}
    service = Mock(side_effect=[graph_result(), httpx.ReadTimeout(secret), RuntimeError(secret)])
    monkeypatch.setattr(arbitration, "evaluate_response", service)

    with TestClient(app) as client:
        response = client.post(URL, json={"items": [*ITEMS, third]})

    assert response.status_code == 200
    assert service.call_count == 3
    results = response.json()["results"]
    assert [item["status"] for item in results] == ["completed", "timed_out", "failed"]
    assert [item["index"] for item in results] == [0, 1, 2]
    assert results[1]["evaluation"] is None
    assert results[1]["error"] == "Evaluation timed out"
    assert results[2]["evaluation"] is None
    assert results[2]["error"] == "Evaluation failed"
    assert secret not in response.text


@pytest.mark.parametrize(
    "timeout",
    [
        TimeoutError("private"),
        httpx.ReadTimeout("private"),
        APITimeoutError(request=httpx.Request("POST", "https://example.invalid")),
    ],
)
def test_batch_classifies_timeout_types(monkeypatch, timeout):
    monkeypatch.setattr(arbitration, "evaluate_response", Mock(side_effect=timeout))

    with TestClient(app) as client:
        response = client.post(URL, json={"items": [ITEMS[0]]})

    assert response.status_code == 200
    assert response.json()["results"][0] == {
        "index": 0, "status": "timed_out", "evaluation": None,
        "error": "Evaluation timed out",
    }


def test_batch_all_failures_and_unusable_result(monkeypatch):
    service = Mock(side_effect=[None, {"verdict": None}])
    monkeypatch.setattr(arbitration, "evaluate_response", service)

    with TestClient(app) as client:
        response = client.post(URL, json={"items": ITEMS})

    assert response.status_code == 200
    assert response.json() == {"results": [
        {"index": 0, "status": "failed", "evaluation": None, "error": "Evaluation failed"},
        {"index": 1, "status": "failed", "evaluation": None, "error": "Evaluation failed"},
    ]}
    assert service.call_count == 2


def test_batch_inconclusive_verdict_is_completed(monkeypatch):
    verdict = VerdictSchema(
        overall_score=1, confidence=0.5, summary="Partial", status="inconclusive"
    )
    result = graph_result(
        verdict=verdict,
        failed_critics=["logic_critic"],
        missing_dimensions=["logic"],
        critiques_complete=False,
        requires_adjudication=False,
        adjudication=None,
    )
    monkeypatch.setattr(arbitration, "evaluate_response", Mock(return_value=result))

    with TestClient(app) as client:
        response = client.post(URL, json={"items": [ITEMS[0]]})

    assert response.status_code == 200
    item = response.json()["results"][0]
    assert item["status"] == "completed"
    assert item["evaluation"]["verdict"] == verdict.model_dump(mode="json")
    assert item["evaluation"]["failed_critics"] == ["logic_critic"]
    assert item["evaluation"]["missing_dimensions"] == ["logic"]


def test_batch_does_not_create_history(monkeypatch, tmp_path):
    path = tmp_path / "arbitrations.sqlite3"
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(path))
    monkeypatch.setattr(arbitration, "evaluate_response", Mock(return_value=graph_result()))

    with TestClient(app) as client:
        response = client.post(URL, json={"items": ITEMS})

    assert response.status_code == 200
    assert not path.exists()
