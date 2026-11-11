"""Offline tests for the evaluation runner (no LLM/API required)."""

import json
from pathlib import Path

from tests.evaluation.evaluate import evaluate_case, main, run_dataset, save_report


DATASET = json.loads(Path(__file__).with_name("dataset.json").read_text(encoding="utf-8"))


def _mock_result(score=5, issues=None):
    issues = issues or []
    return {
        "critiques": [
            {"dimension": dim, "score": score, "issues": issues if dim == "accuracy" else []}
            for dim in ("accuracy", "logic", "completeness")
        ],
        "verdict": {"status": "assessed", "overall_score": 10},
        "adjudication": None,
    }


def test_correct_baseline_passes():
    case = DATASET["cases"][0]
    assert evaluate_case(case, _mock_result())["passed"] is True


def test_out_of_range_score_fails():
    case = DATASET["cases"][0]
    assert evaluate_case(case, _mock_result(score=1))["passed"] is False


def test_missing_dimension_fails():
    case = DATASET["cases"][0]
    outcome = _mock_result()
    outcome["critiques"].pop()
    assert evaluate_case(case, outcome)["passed"] is False


def test_expected_issue_presence():
    case = DATASET["cases"][1]
    result = _mock_result(score=5, issues=[{"severity": "critical", "description": "wrong capital"}])
    for critic in result["critiques"]:
        if critic["dimension"] == "accuracy":
            critic["score"] = 1
    assert evaluate_case(case, result)["passed"] is True


def test_run_and_save_report(tmp_path):
    class MockGraph:
        def invoke(self, state):
            return _mock_result()

    results = run_dataset(MockGraph(), [DATASET["cases"][0]])
    json_path, md_path = save_report(results, tmp_path)
    assert json.loads(json_path.read_text())["passed"] == 1
    assert "Passed: **1/1**" in md_path.read_text()


def test_legacy_case_fields_remain_in_json(tmp_path):
    class MockGraph:
        def invoke(self, state):
            return _mock_result()

    json_path, _ = save_report(run_dataset(MockGraph(), [DATASET["cases"][0]]), tmp_path)
    row = json.loads(json_path.read_text())["cases"][0]
    assert {
        "id", "scenario", "passed", "checks", "observed_scores",
        "observed_issues", "verdict", "adjudication",
        "requires_adjudication", "elapsed_seconds",
    } <= row.keys()


def test_execution_diagnostics_for_complete_partial_and_error():
    case = DATASET["cases"][0]

    class MockGraph:
        def __init__(self, outcome):
            self.outcome = outcome

        def invoke(self, state):
            if isinstance(self.outcome, Exception):
                raise self.outcome
            return self.outcome

    complete = run_dataset(MockGraph(_mock_result()), [case])[0]
    assert complete["case_id"] == case["id"]
    assert complete["execution_status"] == "success"
    assert complete["critique_counts"] == {"accuracy": 1, "logic": 1, "completeness": 1}
    assert complete["failed_critics"] == []
    assert complete["elapsed_seconds"] >= 0

    partial_result = _mock_result()
    partial_result["critiques"] = [c for c in partial_result["critiques"] if c["dimension"] != "logic"]
    partial_result["failed_critics"] = ["logic_critic"]
    partial = run_dataset(MockGraph(partial_result), [case])[0]
    assert partial["execution_status"] == "partial"
    assert partial["critique_counts"]["logic"] == 0
    assert partial["failed_critics"] == ["logic_critic"]
    assert "logic_critic" in partial["failure_reason"]

    error = run_dataset(MockGraph(RuntimeError("api_key=secret")), [case])[0]
    assert error["execution_status"] == "error"
    assert error["failure_reason"] == "RuntimeError during evaluation"
    assert "secret" not in json.dumps(error)
    assert error["elapsed_seconds"] >= 0


def test_failed_logic_critic_is_inconclusive_not_quality_failure():
    case = DATASET["cases"][0]
    result = _mock_result()
    result["critiques"] = [c for c in result["critiques"] if c["dimension"] != "logic"]
    # The graph catches provider exceptions such as GoogleRateLimitError and
    # exposes only failed_critics, not the underlying exception class.
    result["failed_critics"] = ["logic_critic"]
    outcome = evaluate_case(case, result)
    assert outcome["evaluation_pass"] is None
    assert outcome["passed"] is False
    assert outcome["execution_status"] == "partial"
    assert "cause unavailable" in outcome["failure_reason"]


def test_out_of_range_score_is_quality_failure():
    outcome = evaluate_case(DATASET["cases"][0], _mock_result(score=1))
    assert outcome["execution_status"] == "success"
    assert outcome["evaluation_pass"] is False
    assert outcome["passed"] is False


def test_eval_003_score_diagnostic_has_expected_and_observed():
    case = DATASET["cases"][2]
    result = _mock_result()
    result["critiques"][0]["score"] = 1
    outcome = evaluate_case(case, result)
    check = next(c for c in outcome["checks"] if c["name"] == "accuracy_score_range")
    assert outcome["observed_scores"]["accuracy"] == 1
    assert check["expected"] == {"min": 4, "max": 5}
    assert check["observed"] == 1
    assert "actual=1; expected=4..5" in check["details"]


def test_issue_severity_mismatch_shows_observed_issue():
    case = DATASET["cases"][1]
    result = _mock_result(issues=[{"severity": "medium", "description": "Wrong capital"}])
    result["critiques"][0]["score"] = 1
    outcome = evaluate_case(case, result)
    check = next(c for c in outcome["checks"] if c["name"] == "expected_issue_1_dimension_severity")
    assert check["passed"] is False
    assert check["expected"] == {"dimension": "accuracy", "severity": "critical"}
    assert check["observed"] == [{"dimension": "accuracy", "severity": "medium", "description": "Wrong capital"}]
    assert "accuracy/medium: Wrong capital" in check["details"]
    assert "0 candidate(s)" not in check["details"]
    assert "meaning NOT checked" in check["details"]


def test_summary_uses_evaluable_denominator(tmp_path):
    case = DATASET["cases"][0]
    good = evaluate_case(case, _mock_result())
    bad = evaluate_case(case, _mock_result(score=1))
    partial_result = _mock_result()
    partial_result["critiques"].pop()
    partial_result["failed_critics"] = ["completeness_critic"]
    partial = evaluate_case(case, partial_result)
    for row in (good, bad, partial):
        row["elapsed_seconds"] = 0.1

    json_path, _ = save_report([good, bad, partial], tmp_path)
    summary = json.loads(json_path.read_text())
    assert (summary["total"], summary["passed"], summary["failed"], summary["inconclusive"], summary["evaluable"]) == (3, 1, 1, 1, 2)
    assert summary["pass_rate"] == 0.5

    json_path, _ = save_report([partial], tmp_path)
    summary = json.loads(json_path.read_text())
    assert summary["evaluable"] == 0
    assert summary["pass_rate"] is None


def test_markdown_explains_score_severity_and_operational_failure(tmp_path):
    score_case = DATASET["cases"][2]
    score_result = _mock_result()
    score_result["critiques"][0]["score"] = 1
    score_result["critiques"][2]["score"] = 3
    score_result["critiques"][2]["issues"] = [{"severity": "medium", "description": "Missing blue"}]
    quality = evaluate_case(score_case, score_result)

    partial_result = _mock_result()
    partial_result["critiques"] = [c for c in partial_result["critiques"] if c["dimension"] != "logic"]
    partial_result["failed_critics"] = ["logic_critic"]
    inconclusive = evaluate_case(DATASET["cases"][0], partial_result)
    for row in (quality, inconclusive):
        row["elapsed_seconds"] = 0.1

    _, md_path = save_report([quality, inconclusive], tmp_path)
    md = md_path.read_text()
    assert "Passed: **0/1** (0.0%)" in md
    assert "Inconclusive: **1**" in md
    assert "actual=1; expected=4..5" in md
    assert "completeness/high; observed completeness/medium: Missing blue" in md
    assert "logic_critic" in md
    assert "Diagnostic only" in md


def test_cli_exit_code_and_summary_with_mock_graph(tmp_path, monkeypatch, capsys):
    import sys

    class MockGraph:
        def __init__(self, result):
            self.result = result

        def invoke(self, state):
            return self.result

    monkeypatch.setattr(sys, "argv", ["evaluate", "--dataset", str(Path(__file__).with_name("dataset.json")), "--output", str(tmp_path), "--limit", "1"])
    monkeypatch.setattr("src.arbitration.graph.run_agents_graph", lambda: MockGraph(_mock_result()))
    assert main() == 0
    assert "Passed 1/1 evaluable; failed by quality 0; inconclusive 0" in capsys.readouterr().out

    partial = _mock_result()
    partial["critiques"].pop()
    partial["failed_critics"] = ["completeness_critic"]
    monkeypatch.setattr("src.arbitration.graph.run_agents_graph", lambda: MockGraph(partial))
    assert main() == 1
    assert "Passed 0/0 evaluable; failed by quality 0; inconclusive 1" in capsys.readouterr().out
