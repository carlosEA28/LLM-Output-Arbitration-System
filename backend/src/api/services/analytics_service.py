from src.api import arbitration_history
from src.api.schemas.responses import EvaluationResponse
from src.arbitration.schemas.critique import DimensionsEnum


def get_analytics() -> dict:
    arbitrations = {"total": 0, "assessed": 0, "inconclusive": 0}
    critics = {
        dimension.value: {"evaluations": 0, "average_score": 0.0, "issues": 0}
        for dimension in DimensionsEnum
    }
    score_totals = {dimension.value: 0 for dimension in DimensionsEnum}
    adjudication = {"requested": 0, "confirmed_issues": 0, "dismissed_issues": 0}

    for status, evaluation_json in arbitration_history.list_analytics_records():
        arbitrations["total"] += 1
        if status != "completed":
            continue

        evaluation = EvaluationResponse.model_validate_json(evaluation_json)
        arbitrations[evaluation.verdict.status] += 1

        for critique in evaluation.critiques:
            dimension = critique.dimension.value
            critics[dimension]["evaluations"] += 1
            critics[dimension]["issues"] += len(critique.issues)
            score_totals[dimension] += critique.score

        if evaluation.requires_adjudication:
            adjudication["requested"] += 1
        if evaluation.adjudication is not None:
            adjudication["confirmed_issues"] += len(
                evaluation.adjudication.confirmed_issues
            )
            adjudication["dismissed_issues"] += len(
                evaluation.adjudication.dismissed_issues
            )

    for dimension, metrics in critics.items():
        if metrics["evaluations"]:
            metrics["average_score"] = score_totals[dimension] / metrics["evaluations"]

    return {
        "arbitrations": arbitrations,
        "critics": critics,
        "adjudication": adjudication,
    }
