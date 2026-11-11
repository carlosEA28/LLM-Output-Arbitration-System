import unittest

from pydantic import ValidationError

from src.arbitration.schemas.critique import IssueSchema
from src.arbitration.schemas.verdict import AdjudicationSchema, DismissedIssueSchema, VerdictSchema


class VerdictSchemaTests(unittest.TestCase):
    def test_valid_results(self):
        issue = IssueSchema(description="Unsupported claim", severity="high")
        dismissal = DismissedIssueSchema(issue=issue, reason="Contradicted by the response")
        self.assertEqual(AdjudicationSchema(confirmed_issues=[issue], dismissed_issues=[dismissal]).confirmed_issues, [issue])
        verdict = VerdictSchema(overall_score=7, confidence=0.5, confirmed_issues=[issue], dismissed_issues=[dismissal], summary="Limited evidence")
        self.assertEqual(verdict.status, "assessed")

    def test_bounds_and_reason(self):
        issue = IssueSchema(description="Unsupported claim", severity="high")
        for values in ({"overall_score": 0, "confidence": 0.5}, {"overall_score": 11, "confidence": 0.5}, {"overall_score": 5, "confidence": -0.1}, {"overall_score": 5, "confidence": 1.1}):
            with self.subTest(values=values), self.assertRaises(ValidationError):
                VerdictSchema(**values, summary="Summary")
        with self.assertRaises(ValidationError):
            DismissedIssueSchema(issue=issue, reason="")
