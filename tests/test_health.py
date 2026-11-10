from fastapi.testclient import TestClient

from src.api.main import app


def test_health_returns_200_without_model_configuration(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
