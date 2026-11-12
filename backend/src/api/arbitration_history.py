import json
import os
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID, uuid4

from src.api.schemas.responses import EvaluationResponse


def _database_path() -> Path:
    return Path(os.environ.get("ARBITRATION_DB_PATH", "arbitrations.sqlite3"))


@contextmanager
def _connect():
    with closing(sqlite3.connect(_database_path(), timeout=5)) as connection:
        connection.row_factory = sqlite3.Row
        with connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS arbitrations (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    original_question TEXT NOT NULL,
                    generated_output TEXT,
                    evaluation_json TEXT
                )
                """
            )
            yield connection


def create(original_question: str) -> UUID:
    arbitration_id = uuid4()
    with _connect() as connection:
        connection.execute(
            """INSERT INTO arbitrations (id, created_at, status, original_question)
               VALUES (?, ?, ?, ?)""",
            (
                str(arbitration_id),
                datetime.now(timezone.utc).isoformat(),
                "pending",
                original_question,
            ),
        )
    return arbitration_id


def save_generated_output(arbitration_id: UUID, generated_output: str) -> None:
    with _connect() as connection:
        connection.execute(
            "UPDATE arbitrations SET generated_output = ? WHERE id = ?",
            (generated_output, str(arbitration_id)),
        )


def complete(arbitration_id: UUID, evaluation: EvaluationResponse) -> None:
    with _connect() as connection:
        connection.execute(
            "UPDATE arbitrations SET status = ?, evaluation_json = ? WHERE id = ?",
            ("completed", evaluation.model_dump_json(), str(arbitration_id)),
        )


def fail(arbitration_id: UUID, *, timed_out: bool) -> None:
    with _connect() as connection:
        connection.execute(
            "UPDATE arbitrations SET status = ? WHERE id = ?",
            ("timed_out" if timed_out else "failed", str(arbitration_id)),
        )


def get(arbitration_id: UUID) -> dict | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT * FROM arbitrations WHERE id = ?", (str(arbitration_id),)
        ).fetchone()
    if row is None:
        return None
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "status": row["status"],
        "original_question": row["original_question"],
        "generated_output": row["generated_output"],
        "evaluation": (
            json.loads(row["evaluation_json"]) if row["evaluation_json"] else None
        ),
    }


def list_analytics_records() -> list[tuple[str, str | None]]:
    with _connect() as connection:
        rows = connection.execute(
            "SELECT status, evaluation_json FROM arbitrations"
        ).fetchall()
    return [(row["status"], row["evaluation_json"]) for row in rows]
