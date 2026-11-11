
from src.arbitration.schemas.verdict import VerdictSchema
from src.arbitration.states import ArbitrationState


def synthesize_verdict(state: ArbitrationState) -> dict:
    critiques = state.get("critiques", [])

    if not critiques:
        return {
            "verdict": VerdictSchema(
                overall_score=1,
                confidence=0.0,
                summary="Inconclusive: no critic evaluations available.",
                status="inconclusive",
            )
        }

    adjudication = state.get("adjudication")

    confirmed_keys = (
        {issue.model_dump_json() for issue in adjudication.confirmed_issues}
        if adjudication else set()
    )

    dismissed = adjudication.dismissed_issues if adjudication else []
    dismissed_keys = {
        item.issue.model_dump_json() for item in dismissed
    }

    confirmed = []
    unverified = []
    seen = set()

    for critique in critiques:
        for issue in critique.issues:
            key = issue.model_dump_json()

            if key in seen:
                continue

            seen.add(key)

            if key in confirmed_keys:
                confirmed.append(issue)
            elif key not in dismissed_keys:
                unverified.append(issue)

    scores = {
        critique.dimension.value: critique.score
        for critique in critiques
    }

    average = sum(scores.values()) / len(scores)
    overall_score = round(1 + (average - 1) * 9 / 4)

    # Prevent critical issues from being hidden by the average.
    if any(
        issue.severity.value == "critical"
        for issue in confirmed + unverified
    ):
        overall_score = min(overall_score, 4)

    # Heuristic coverage indicator, not calibrated probability.
    confidence = 0.75 * len(scores) / 3

    incomplete = (
        len(scores) < 3
        or bool(state.get("failed_critics"))
        or bool(state.get("duplicate_dimensions"))
    )

    if incomplete:
        confidence = min(confidence, 0.5)

    summary = (
        f"Evaluated {len(scores)} of 3 dimensions. "
        f"Found {len(confirmed)} confirmed, "
        f"{len(dismissed)} dismissed, "
        f"and {len(unverified)} unverified issues."
    )

    return {
        "verdict": VerdictSchema(
            overall_score=overall_score,
            confidence=confidence,
            confirmed_issues=confirmed,
            dismissed_issues=dismissed,
            unverified_issues=unverified,
            summary=summary,
            status="inconclusive" if incomplete else "assessed",
        )
    }
