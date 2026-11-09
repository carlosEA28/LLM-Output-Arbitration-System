"""Offline tests for the evaluation runner (no LLM/API required)."""

import json
from pathlib import Path

from tests.evaluation.evaluate import evaluate_case, run_dataset, save_report


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
