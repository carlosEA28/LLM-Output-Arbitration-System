
import pytest

from src.arbitration.schemas.critique import (
    CritiqueSchema,
    DimensionsEnum,
    IssueSchema,
    SeverityEnum,
)
from src.arbitration.schemas.verdict import (
    AdjudicationSchema,
    DismissedIssueSchema,
)
from src.arbitration.graph import route_after_disagreements
from src.nodes.adjudicator import adjudicator, validate_adjudication
from src.nodes.synthesize_verdict import synthesize_verdict


def make_issue(description: str) -> IssueSchema:
    return IssueSchema(
        quote="The capital of France is Paris.",
        description=description,
        severity=SeverityEnum.high,
    )


def make_state(
    response: str,
    issue: IssueSchema,
    score: int = 2,
) -> dict:
    return {
        "original_question": "What is the capital of France?",
        "generated_output": response,
        "critiques": [
            CritiqueSchema(
                dimension=DimensionsEnum.accuracy,
                score=score,
                issues=[issue],
                confidence=0.9,
            )
        ],
        "disagreements": [
            "accuracy: Inconsistent evaluation requiring review."
        ],
        "requires_adjudication": True,
        "failed_critics": [],
        "duplicate_dimensions": [],
        "critiques_complete": False,
    }


# Test 1 - Confirm a valid issue
def test_confirm_issue():
    issue = IssueSchema(
        quote="The capital of France is Berlin.",
        description="The capital of France is Paris, not Berlin.",
        severity=SeverityEnum.high,
    )

    state = make_state(
        response="The capital of France is Berlin.",
        issue=issue,
    )

    assessment = adjudicator(state)["adjudication"]

    assert assessment is not None
    assert issue in assessment.confirmed_issues
    assert not assessment.dismissed_issues


# Test 2 - Dismiss an incorrect issue
def test_dismiss_issue():
    issue = make_issue("Paris is not the capital of France.")

    state = make_state(
        response="The capital of France is Paris.",
        issue=issue,
    )

    assessment = adjudicator(state)["adjudication"]

    assert assessment is not None
    assert any(
        item.issue == issue
        for item in assessment.dismissed_issues
    )
    assert issue not in assessment.confirmed_issues


# Test 3 - Preserve uncertainty
def test_uncertain_issue():
    issue = IssueSchema(
        quote="The company's internal revenue increased by 37%.",
        description="The revenue figure may be incorrect.",
        severity=SeverityEnum.medium,
    )

    state = make_state(
        response="The company's internal revenue increased by 37%.",
        issue=issue,
    )

    state["original_question"] = (
        "How much did the company's internal revenue increase?"
    )

    assessment = adjudicator(state)["adjudication"]

    assert assessment is not None
    assert issue not in assessment.confirmed_issues
    assert all(
        item.issue != issue
        for item in assessment.dismissed_issues
    )


# Test 4 - Verdict with a confirmed issue
def test_verdict_confirmed():
    issue = make_issue("Incorrect factual information.")
    state = make_state("The capital of France is Paris.", issue)

    state["adjudication"] = AdjudicationSchema(
        confirmed_issues=[issue]
    )

    verdict = synthesize_verdict(state)["verdict"]

    assert issue in verdict.confirmed_issues
    assert issue not in verdict.unverified_issues


# Test 5 - Verdict with a dismissed issue
def test_verdict_dismissed():
    issue = make_issue("Paris is not the capital of France.")
    state = make_state("The capital of France is Paris.", issue)

    state["adjudication"] = AdjudicationSchema(
        dismissed_issues=[
            DismissedIssueSchema(
                issue=issue,
                reason="Paris is the capital of France.",
            )
        ]
    )

    verdict = synthesize_verdict(state)["verdict"]

    assert len(verdict.dismissed_issues) == 1
    assert issue not in verdict.confirmed_issues
    assert issue not in verdict.unverified_issues


# Test 6 - Verdict without adjudication
def test_verdict_unverified():
    issue = make_issue("Potential factual error.")
    state = make_state("The capital of France is Paris.", issue)

    state["adjudication"] = None

    verdict = synthesize_verdict(state)["verdict"]

    assert issue in verdict.unverified_issues
    assert not verdict.confirmed_issues


# Test 7 - All critics fail
def test_all_critics_failed():
    state = {
        "critiques": [],
        "failed_critics": [
            "accuracy_critic",
            "logic_critic",
            "completeness_critic",
        ],
    }

    verdict = synthesize_verdict(state)["verdict"]

    assert verdict.status == "inconclusive"
    assert verdict.confidence == 0.0


# Test 8 - Conditional routing
def test_conditional_routing():
    assert route_after_disagreements({
        "requires_adjudication": True
    }) == "adjudicator"

    assert route_after_disagreements({
        "requires_adjudication": False
    }) == "synthesize_verdict"


# Test 9 - Reject invented issues
def test_reject_invented_issue():
    issue = make_issue("Original issue.")
    state = make_state("The capital of France is Paris.", issue)

    invented = IssueSchema(
        description="Invented issue.",
        severity=SeverityEnum.low,
    )

    result = AdjudicationSchema(
        confirmed_issues=[invented]
    )

    with pytest.raises(ValueError):
        validate_adjudication(result, state["critiques"])


# Test 10 - Reject contradictory decisions
def test_reject_contradictory_decisions():
    issue = make_issue("Original issue.")
    state = make_state("The capital of France is Paris.", issue)

    result = AdjudicationSchema(
        confirmed_issues=[issue],
        dismissed_issues=[
            DismissedIssueSchema(
                issue=issue,
                reason="No basis for this issue.",
            )
        ],
    )

    with pytest.raises(ValueError):
        validate_adjudication(result, state["critiques"])


# Test 11 - Allow undecided issues
def test_allow_undecided_issue():
    issue = make_issue("Potential factual error.")
    state = make_state("The capital of France is Paris.", issue)

    result = AdjudicationSchema()

    validate_adjudication(result, state["critiques"])
