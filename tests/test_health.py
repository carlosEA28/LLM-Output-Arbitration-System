import os
import subprocess
import sys

from fastapi.testclient import TestClient

from src.api.main import app


def test_health_returns_200_without_model_configuration(monkeypatch, tmp_path):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    database = tmp_path / "arbitrations.sqlite3"
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(database))

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert not database.exists()


def test_import_does_not_create_history_database(tmp_path):
    database = tmp_path / "arbitrations.sqlite3"
    result = subprocess.run(
        [sys.executable, "-c", "import src.api.main"],
        env={**os.environ, "ARBITRATION_DB_PATH": str(database)},
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert not database.exists()
