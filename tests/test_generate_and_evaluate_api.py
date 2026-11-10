from unittest.mock import Mock

import pytest
import httpx
from fastapi.testclient import TestClient
from openai import APITimeoutError

from src.api.main import app
from src.api.routes import arbitration
from src.api.services import arbitration_service
from src.arbitration.schemas.verdict import VerdictSchema
from tests.test_evaluate_api import graph_result


def test_generate_and_evaluate_returns_answer_and_structured_result(monkeypatch):
    result = graph_result()
    result["generated_output"] = "Generated answer."
    service = Mock(return_value=result)
    monkeypatch.setattr(arbitration, "generate_and_evaluate", service)

    with TestClient(app) as client:
        response = client.post(
            "/generate-and-evaluate", json={"original_question": "Question?"}
        )

    assert response.status_code == 200
    service.assert_called_once_with("Question?")
    body = response.json()
    assert set(body) == set(result)
    assert body["generated_output"] == "Generated answer."
    assert body["critiques"] == [result["critiques"][0].model_dump(mode="json")]
    assert body["adjudication"] == result["adjudication"].model_dump(mode="json")
    assert body["verdict"] == result["verdict"].model_dump(mode="json")


def test_generate_and_evaluate_preserves_direct_inconclusive_result(monkeypatch):
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
        verdict=verdict,
        generated_output="Generated answer.",
    )
    result.pop("adjudication")
    monkeypatch.setattr(arbitration, "generate_and_evaluate", Mock(return_value=result))

    with TestClient(app) as client:
        response = client.post(
            "/generate-and-evaluate", json={"original_question": "Question?"}
        )

    assert response.status_code == 200
    body = response.json()
    assert body["generated_output"] == "Generated answer."
    assert body["failed_critics"] == ["logic_critic"]
    assert body["missing_dimensions"] == ["logic"]
    assert body["critiques_complete"] is False
    assert body["adjudication"] is None
    assert body["verdict"] == verdict.model_dump(mode="json")


@pytest.mark.parametrize(
    "payload",
    [{}, {"original_question": 3}, {"original_question": ""}, {"original_question": " \t "}],
)
def test_invalid_question_returns_422_without_service(monkeypatch, payload):
    service = Mock()
    monkeypatch.setattr(arbitration, "generate_and_evaluate", service)

    with TestClient(app) as client:
        response = client.post("/generate-and-evaluate", json=payload)

    assert response.status_code == 422
    service.assert_not_called()


def test_invalid_question_does_not_echo_private_payload(monkeypatch):
    service = Mock()
    monkeypatch.setattr(arbitration, "generate_and_evaluate", service)

    with TestClient(app) as client:
        response = client.post(
            "/generate-and-evaluate",
            json={"original_question": {"secret": "private prompt and credential"}},
        )

    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid request"}
    assert "private prompt and credential" not in response.text
    service.assert_not_called()


@pytest.mark.parametrize(
    "generated",
    [RuntimeError("provider-token-and-model-payload"), " \t "],
)
def test_generation_failure_is_private_and_skips_evaluation(monkeypatch, generated):
    generator = Mock()
    if isinstance(generated, Exception):
        generator.side_effect = generated
    else:
        generator.return_value = generated
    evaluation = Mock()
    monkeypatch.setattr(arbitration_service, "generate_response", generator)
    monkeypatch.setattr(arbitration_service, "evaluate_response", evaluation)

    with TestClient(app) as client:
        response = client.post(
            "/generate-and-evaluate", json={"original_question": "Question?"}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Generation and evaluation failed"}
    assert "provider-token-and-model-payload" not in response.text
    generator.assert_called_once_with("Question?")
    evaluation.assert_not_called()


def test_arbitration_failure_is_private(monkeypatch):
    generator = Mock(return_value="Generated answer.")
    evaluation = Mock(side_effect=RuntimeError("provider-token-and-model-payload"))
    monkeypatch.setattr(arbitration_service, "generate_response", generator)
    monkeypatch.setattr(arbitration_service, "evaluate_response", evaluation)

    with TestClient(app) as client:
        response = client.post(
            "/generate-and-evaluate", json={"original_question": "Question?"}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Generation and evaluation failed"}
    assert "provider-token-and-model-payload" not in response.text
    evaluation.assert_called_once_with("Question?", "Generated answer.")


@pytest.mark.parametrize(
    "timeout",
    [
        TimeoutError("token=private prompt=hidden provider traceback"),
        httpx.ReadTimeout("token=private prompt=hidden provider traceback"),
        APITimeoutError(request=httpx.Request("POST", "https://example.invalid")),
    ],
)
def test_generation_timeout_is_safe_and_skips_arbitration(monkeypatch, timeout):
    generator = Mock(side_effect=timeout)
    evaluation = Mock()
    monkeypatch.setattr(arbitration_service, "generate_response", generator)
    monkeypatch.setattr(arbitration_service, "evaluate_response", evaluation)

    with TestClient(app) as client:
        response = client.post(
            "/generate-and-evaluate", json={"original_question": "Question?"}
        )

    assert response.status_code == 504
    assert response.json() == {"detail": "Generation and evaluation timed out"}
    assert "token=private" not in response.text
    assert "prompt=hidden" not in response.text
    assert "traceback" not in response.text
    evaluation.assert_not_called()


def test_arbitration_timeout_after_generation_is_safe(monkeypatch):
    generator = Mock(return_value="Generated answer.")
    evaluation = Mock(side_effect=TimeoutError("token=private prompt=hidden provider traceback"))
    monkeypatch.setattr(arbitration_service, "generate_response", generator)
    monkeypatch.setattr(arbitration_service, "evaluate_response", evaluation)

    with TestClient(app) as client:
        response = client.post(
            "/generate-and-evaluate", json={"original_question": "Question?"}
        )

    assert response.status_code == 504
    assert response.json() == {"detail": "Generation and evaluation timed out"}
    assert "token=private" not in response.text
    assert "prompt=hidden" not in response.text
    assert "traceback" not in response.text
    evaluation.assert_called_once_with("Question?", "Generated answer.")


@pytest.mark.parametrize("result", [None, {"generated_output": "Answer.", "verdict": None}])
def test_invalid_verdict_returns_generic_error(monkeypatch, result):
    monkeypatch.setattr(arbitration, "generate_and_evaluate", Mock(return_value=result))

    with TestClient(app) as client:
        response = client.post(
            "/generate-and-evaluate", json={"original_question": "Question?"}
        )

    assert response.status_code == 500
    assert response.json() == {"detail": "Generation and evaluation failed"}
