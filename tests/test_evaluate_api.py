from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.routes import arbitration
from src.arbitration.schemas.critique import CritiqueSchema, IssueSchema
from src.arbitration.schemas.verdict import AdjudicationSchema, VerdictSchema


REQUEST = {"original_question": "Question?", "generated_output": "Existing answer."}


def graph_result(**overrides):
    issue = IssueSchema(description="Unsupported claim", severity="high")
    result = {
        "critiques": [
            CritiqueSchema(
                dimension="accuracy", score=2, issues=[issue], confidence=0.9
            )
        ],
        "failed_critics": [],
        "missing_dimensions": [],
        "duplicate_dimensions": [],
        "critiques_complete": True,
        "disagreements": [],
        "requires_adjudication": True,
        "adjudication": AdjudicationSchema(confirmed_issues=[issue]),
        "verdict": VerdictSchema(
            overall_score=4,
            confidence=0.75,
            confirmed_issues=[issue],
            summary="Controlled evaluation",
            status="assessed",
        ),
    }
    result.update(overrides)
    return result


def test_evaluate_returns_structured_graph_result(monkeypatch):
    result = graph_result()
    service = Mock(return_value=result)
    monkeypatch.setattr(arbitration, "evaluate_response", service)

    with TestClient(app) as client:
        response = client.post("/evaluate", json=REQUEST)

    assert response.status_code == 200
    service.assert_called_once_with("Question?", "Existing answer.")
    body = response.json()
    assert set(body) == {
        "critiques", "failed_critics", "missing_dimensions",
        "duplicate_dimensions", "critiques_complete", "disagreements",
        "requires_adjudication", "adjudication", "verdict",
    }
    assert body["critiques"] == [result["critiques"][0].model_dump(mode="json")]
    assert body["adjudication"] == result["adjudication"].model_dump(mode="json")
    assert body["verdict"] == result["verdict"].model_dump(mode="json")


def test_evaluate_returns_null_when_graph_skips_adjudication(monkeypatch):
    result = graph_result(requires_adjudication=False)
    result.pop("adjudication")
    monkeypatch.setattr(arbitration, "evaluate_response", Mock(return_value=result))

    with TestClient(app) as client:
        response = client.post("/evaluate", json=REQUEST)

    assert response.status_code == 200
    assert response.json()["adjudication"] is None
    assert response.json()["verdict"] == result["verdict"].model_dump(mode="json")


def test_evaluate_preserves_partial_inconclusive_result(monkeypatch):
    verdict = VerdictSchema(
        overall_score=1,
        confidence=0.5,
        summary="One critic unavailable",
        status="inconclusive",
    )
    result = graph_result(
        failed_critics=["logic_critic"],
        missing_dimensions=["logic"],
        critiques_complete=False,
        requires_adjudication=False,
        adjudication=None,
        verdict=verdict,
    )
    monkeypatch.setattr(arbitration, "evaluate_response", Mock(return_value=result))

    with TestClient(app) as client:
        response = client.post("/evaluate", json=REQUEST)

    assert response.status_code == 200
    body = response.json()
    assert body["critiques"] == [result["critiques"][0].model_dump(mode="json")]
    assert body["failed_critics"] == ["logic_critic"]
    assert body["missing_dimensions"] == ["logic"]
    assert body["critiques_complete"] is False
    assert body["verdict"] == verdict.model_dump(mode="json")


@pytest.mark.parametrize("result", [None, {"verdict": None}])
def test_evaluate_returns_generic_error_for_invalid_verdict(monkeypatch, result):
    monkeypatch.setattr(arbitration, "evaluate_response", Mock(return_value=result))

    with TestClient(app) as client:
        response = client.post("/evaluate", json=REQUEST)

    assert response.status_code == 500
    assert response.json() == {"detail": "Evaluation failed"}


def test_evaluate_does_not_expose_graph_exception(monkeypatch):
    secret = "provider-token-and-sensitive-payload"
    service = Mock(side_effect=RuntimeError(secret))
    monkeypatch.setattr(arbitration, "evaluate_response", service)

    with TestClient(app) as client:
        response = client.post("/evaluate", json=REQUEST)

    assert response.status_code == 500
    assert response.json() == {"detail": "Evaluation failed"}
    assert secret not in response.text


@pytest.mark.parametrize(
    "payload",
    [
        {"generated_output": "Answer."},
        {"original_question": "Question?"},
        {"original_question": "", "generated_output": "Answer."},
        {"original_question": "Question?", "generated_output": " \t "},
        {"original_question": 3, "generated_output": "Answer."},
    ],
)
def test_invalid_input_returns_422_without_graph_execution(monkeypatch, payload):
    service = Mock()
    monkeypatch.setattr(arbitration, "evaluate_response", service)

    with TestClient(app) as client:
        response = client.post("/evaluate", json=payload)

    assert response.status_code == 422
    service.assert_not_called()
