from src.api import arbitration_history
from src.api.schemas.responses import EvaluationResponse
from src.api.services.analytics_service import get_analytics
from src.arbitration.schemas.critique import CritiqueSchema, IssueSchema
from src.arbitration.schemas.verdict import (
    AdjudicationSchema,
    DismissedIssueSchema,
    VerdictSchema,
)
from tests.test_evaluate_api import graph_result


def _save(evaluation):
    arbitration_id = arbitration_history.create("Question?")
    arbitration_history.complete(
        arbitration_id, EvaluationResponse.model_validate(evaluation)
    )


def test_analytics_aggregates_completed_evaluations_and_all_record_statuses(
    monkeypatch, tmp_path
):
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(tmp_path / "arbitrations.sqlite3"))
    issue = IssueSchema(description="Issue", severity="high")
    dismissed = DismissedIssueSchema(issue=issue, reason="Not supported")
    _save(graph_result(
        critiques=[
            CritiqueSchema(dimension="accuracy", score=2, issues=[issue], confidence=0.9),
            CritiqueSchema(dimension="logic", score=4, issues=[], confidence=0.9),
            CritiqueSchema(dimension="accuracy", score=4, issues=[issue, issue], confidence=0.9),
        ],
        adjudication=AdjudicationSchema(
            confirmed_issues=[issue, issue], dismissed_issues=[dismissed]
        ),
    ))
    _save(graph_result(
        critiques=[
            CritiqueSchema(dimension="logic", score=2, issues=[issue], confidence=0.9)
        ],
        requires_adjudication=True,
        adjudication=None,
        verdict=VerdictSchema(
            overall_score=1, confidence=0.5, summary="Partial", status="inconclusive"
        ),
    ))
    arbitration_history.create("Pending?")
    failed_id = arbitration_history.create("Failed?")
    arbitration_history.fail(failed_id, timed_out=False)
    timed_out_id = arbitration_history.create("Timed out?")
    arbitration_history.fail(timed_out_id, timed_out=True)

    result = get_analytics()

    assert result == {
        "arbitrations": {"total": 5, "assessed": 1, "inconclusive": 1},
        "critics": {
            "accuracy": {"evaluations": 2, "average_score": 3.0, "issues": 3},
            "logic": {"evaluations": 2, "average_score": 3.0, "issues": 1},
            "completeness": {"evaluations": 0, "average_score": 0.0, "issues": 0},
        },
        "adjudication": {"requested": 2, "confirmed_issues": 2, "dismissed_issues": 1},
    }


def test_analytics_empty_database_has_all_zero_metrics(monkeypatch, tmp_path):
    monkeypatch.setenv("ARBITRATION_DB_PATH", str(tmp_path / "arbitrations.sqlite3"))

    assert get_analytics() == {
        "arbitrations": {"total": 0, "assessed": 0, "inconclusive": 0},
        "critics": {
            dimension: {"evaluations": 0, "average_score": 0.0, "issues": 0}
            for dimension in ("accuracy", "logic", "completeness")
        },
        "adjudication": {"requested": 0, "confirmed_issues": 0, "dismissed_issues": 0},
    }
