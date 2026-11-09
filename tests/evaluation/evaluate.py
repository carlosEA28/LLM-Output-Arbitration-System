"""Run the LangGraph arbitration graph against the evaluation dataset.

From repository root:
    uv run python -m tests.evaluation.evaluate --limit 3
    uv run python -m tests.evaluation.evaluate

Reports are written to reports/evaluation/ by default.
This is a rule-based baseline; it does not semantically judge free-text issues.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DATASET = Path(__file__).with_name("dataset.json")
REPORT_DIR = Path("reports/evaluation")
DIMENSIONS = ("accuracy", "logic", "completeness")


def as_dict(value: Any) -> dict[str, Any]:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return value
    raise TypeError(f"Expected a Pydantic model or dict, got {type(value).__name__}")


def dimension_name(value: Any) -> str:
    return str(getattr(value, "value", value))


def evaluate_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """Deterministic contract/score and issue-presence checks only."""
    checks: list[dict[str, Any]] = []
    critiques = [as_dict(item) for item in result.get("critiques", [])]
    by_dimension: dict[str, list[dict[str, Any]]] = {dim: [] for dim in DIMENSIONS}

    for critique in critiques:
        dim = dimension_name(critique.get("dimension"))
        if dim in by_dimension:
            by_dimension[dim].append(critique)
        else:
            checks.append({"name": "unexpected_dimension", "passed": False, "details": dim})

    for dim in DIMENSIONS:
        matches = by_dimension[dim]
        checks.append({
            "name": f"{dim}_exactly_once",
            "passed": len(matches) == 1,
            "details": f"received {len(matches)} critique(s)",
        })
        if len(matches) != 1:
            continue
        bounds = case["expected_scores"][dim]
        actual = matches[0].get("score")
        valid = isinstance(actual, (int, float)) and not isinstance(actual, bool)
        checks.append({
            "name": f"{dim}_score_range",
            "passed": bool(valid and bounds["min"] <= actual <= bounds["max"]),
            "details": f"actual={actual}; expected={bounds['min']}..{bounds['max']}",
        })

    all_issues: list[dict[str, Any]] = []
    for critique in critiques:
        dim = dimension_name(critique.get("dimension"))
        for issue in critique.get("issues", []):
            item = as_dict(issue)
            all_issues.append({"dimension": dim, **item})

    # These checks only confirm dimension/severity, NOT semantic correspondence
    # between the issue descriptions. This avoids false claims of semantic eval.
    for index, expected in enumerate(case.get("expected_issues", []), 1):
        if expected.get("optional"):
            continue
        matching = [
            issue for issue in all_issues
            if issue["dimension"] == expected["dimension"]
            and dimension_name(issue.get("severity")) == expected["severity"]
        ]
        checks.append({
            "name": f"expected_issue_{index}_dimension_severity",
            "passed": bool(matching),
            "details": f"expected {expected['dimension']}/{expected['severity']}; found {len(matching)} candidate(s); meaning NOT checked",
        })

    # For cases with no expected issues, require no issues at all.
    if not case.get("expected_issues"):
        checks.append({
            "name": "no_unexpected_issues",
            "passed": not all_issues,
            "details": f"observed {len(all_issues)} issue(s)",
        })

    verdict = result.get("verdict")
    verdict_data = as_dict(verdict) if verdict is not None else None
    checks.append({
        "name": "valid_verdict_present",
        "passed": bool(verdict_data and verdict_data.get("status") in ("assessed", "inconclusive")),
        "details": verdict_data.get("status") if verdict_data else "missing verdict",
    })

    return {
        "id": case["id"],
        "scenario": case["scenario"],
        "passed": all(item["passed"] for item in checks),
        "checks": checks,
        "observed_scores": {
            dim: by_dimension[dim][0].get("score") if len(by_dimension[dim]) == 1 else None
            for dim in DIMENSIONS
        },
        "observed_issues": all_issues,
        "verdict": verdict_data,
        "adjudication": as_dict(result["adjudication"]) if result.get("adjudication") is not None else None,
        "requires_adjudication": result.get("requires_adjudication"),
    }


def run_dataset(graph: Any, cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for case in cases:
        start = time.perf_counter()
        try:
            state = {
                "original_question": case["original_question"],
                "generated_output": case["generated_output"],
                "critiques": [],
                "failed_critics": [],
                "disagreements": [],
                "requires_adjudication": False,
                "adjudication": None,
                "verdict": None,
                "missing_dimensions": [],
                "duplicate_dimensions": [],
                "critiques_complete": False,
            }
            result = evaluate_case(case, graph.invoke(state))
        except Exception as exc:
            result = {
                "id": case["id"],
                "scenario": case["scenario"],
                "passed": False,
                "checks": [],
                "error": f"{type(exc).__name__}: {exc}",
            }
        result["elapsed_seconds"] = round(time.perf_counter() - start, 3)
        results.append(result)
        print(f"{'PASS' if result['passed'] else 'FAIL'} {case['id']} - {case['scenario']}")
    return results


def save_report(results: list[dict[str, Any]], target: Path) -> tuple[Path, Path]:
    target.mkdir(parents=True, exist_ok=True)
    count = len(results)
    passed = sum(bool(row["passed"]) for row in results)
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total": count,
        "passed": passed,
        "failed": count - passed,
        "pass_rate": round(passed / count, 4) if count else 0.0,
        "evaluation_method": "deterministic baseline: score ranges + issue dimension/severity presence (NOT semantic matching)",
        "cases": results,
    }
    json_path = target / "results.json"
    md_path = target / "summary.md"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# LLM Arbitration — Evaluation Results", "",
        f"Passed: **{passed}/{count}** ({summary['pass_rate']:.1%})", "",
        "This is a rule-based baseline. Issue meanings and factual correctness are **not** independently evaluated.",
        "", "| Case | Result | Time (s) |", "|---|---|---:|",
    ]
    for item in results:
        lines.append(f"| {item['id']} | {'PASS' if item['passed'] else 'FAIL'} | {item['elapsed_seconds']:.3f} |")
    lines.append("")
    for item in results:
        if item["passed"]:
            continue
        lines.append(f"## {item['id']}: {item['scenario']}")
        if "error" in item:
            lines.append(f"- Error: `{item['error']}`")
        for check in item.get("checks", []):
            if not check["passed"]:
                lines.append(f"- {check['name']}: {check['details']}")
        lines.append("")
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, md_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate LLM arbitration graph on reference cases")
    parser.add_argument("--dataset", type=Path, default=DATASET)
    parser.add_argument("--output", type=Path, default=REPORT_DIR)
    parser.add_argument("--limit", type=int, default=None, help="Run first N cases (recommended for initial smoke test)")
    args = parser.parse_args()
    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    cases = dataset["cases"][:args.limit] if args.limit is not None else dataset["cases"]
    if not cases:
        parser.error("No cases selected")

    from src.arbitration.graph import run_agents_graph

    graph = run_agents_graph()
    results = run_dataset(graph, cases)
    json_file, md_file = save_report(results, args.output)
    print(f"\nPassed {sum(r['passed'] for r in results)}/{len(results)}")
    print(f"Reports: {json_file} | {md_file}")
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
