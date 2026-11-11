import unittest

from src.arbitration.schemas.critique import CritiqueSchema, IssueSchema
from src.arbitration.schemas.verdict import AdjudicationSchema, DismissedIssueSchema, VerdictSchema
from src.nodes.synthesize_verdict import synthesize_verdict


def critique(dimension, score, *issues):
    return CritiqueSchema(dimension=dimension, score=score, confidence=1.0, issues=list(issues))


class SynthesizeVerdictTests(unittest.TestCase):
    def setUp(self):
        self.factual = IssueSchema(description="False capital", severity="critical")
        self.omission = IssueSchema(description="Missing explanation", severity="medium")
        self.other = IssueSchema(description="Unclear wording", severity="low")

    def test_direct_route_preserves_factual_issue_and_reduces_partial_confidence(self):
        state = {"critiques": [critique("accuracy", 1, self.factual), critique("completeness", 5)],
                 "failed_critics": ["logic_critic"], "missing_dimensions": ["logic"]}
        verdict = synthesize_verdict(state)["verdict"]
        self.assertIsInstance(verdict, VerdictSchema)
        self.assertEqual(verdict.confirmed_issues, [])
        self.assertEqual(verdict.dismissed_issues, [])
        self.assertEqual(verdict.unverified_issues, [self.factual])
        self.assertEqual(verdict.overall_score, 4)
        self.assertEqual(verdict.confidence, 0.5)
        self.assertIn("0 confirmed, 0 dismissed, and 1 unverified", verdict.summary)

    def test_adjudicated_route_preserves_undecided_issue(self):
        state = {"critiques": [critique("accuracy", 2, self.factual, self.omission, self.other)],
                 "adjudication": AdjudicationSchema(confirmed_issues=[self.factual], dismissed_issues=[
                     DismissedIssueSchema(issue=self.omission, reason="Not requested")])}
        verdict = synthesize_verdict(state)["verdict"]
        self.assertEqual(verdict.confirmed_issues, [self.factual])
        self.assertEqual(verdict.dismissed_issues[0].reason, "Not requested")
        self.assertEqual(verdict.unverified_issues, [self.other])
        self.assertEqual(verdict.overall_score, 3)
        self.assertEqual(verdict.confidence, 0.25)
        self.assertIn("1 confirmed, 1 dismissed, and 1 unverified", verdict.summary)

    def test_unverified_critical_issue_limits_score_after_adjudication(self):
        state = {"critiques": [critique("accuracy", 5, self.factual, self.omission)],
                 "adjudication": AdjudicationSchema(confirmed_issues=[self.omission])}
        verdict = synthesize_verdict(state)["verdict"]
        self.assertEqual(verdict.confirmed_issues, [self.omission])
        self.assertEqual(verdict.unverified_issues, [self.factual])
        self.assertEqual(verdict.overall_score, 4)

    def test_dismissed_critical_issue_does_not_limit_score(self):
        dismissal = DismissedIssueSchema(issue=self.factual, reason="Not a defect")
        state = {"critiques": [critique("accuracy", 5, self.factual)],
                 "adjudication": AdjudicationSchema(dismissed_issues=[dismissal])}
        verdict = synthesize_verdict(state)["verdict"]
        self.assertEqual(verdict.confirmed_issues, [])
        self.assertEqual(verdict.dismissed_issues, [dismissal])
        self.assertEqual(verdict.unverified_issues, [])
        self.assertEqual(verdict.overall_score, 10)

    def test_duplicate_critic_issues_appear_once(self):
        state = {"critiques": [critique("accuracy", 5, self.factual), critique("logic", 5, self.factual)]}
        verdict = synthesize_verdict(state)["verdict"]
        self.assertEqual(verdict.unverified_issues, [self.factual])
        self.assertIn("1 unverified", verdict.summary)

    def test_complete_and_duplicate_dimensions(self):
        complete = {"critiques": [critique("accuracy", 5), critique("logic", 5), critique("completeness", 5)]}
        self.assertEqual(synthesize_verdict(complete)["verdict"].confidence, 0.75)
        duplicate = {"critiques": complete["critiques"] + [critique("accuracy", 1)], "duplicate_dimensions": ["accuracy"]}
        verdict = synthesize_verdict(duplicate)["verdict"]
        self.assertEqual(verdict.confidence, 0.5)
        self.assertEqual(verdict.overall_score, 7)

    def test_status_is_assessed_when_critiques_exist(self):
        critiques = [critique("accuracy", 5)]
        for complete in (False, True):
            with self.subTest(critiques_complete=complete):
                verdict = synthesize_verdict({"critiques": critiques, "critiques_complete": complete})["verdict"]
                self.assertEqual(verdict.status, "assessed")

    def test_no_critiques_is_inconclusive(self):
        verdict = synthesize_verdict({"critiques": [], "failed_critics": ["accuracy_critic"]})["verdict"]
        self.assertEqual(verdict.status, "inconclusive")
        self.assertEqual(verdict.overall_score, 1)
        self.assertEqual(verdict.confidence, 0)
        self.assertEqual(verdict.confirmed_issues, [])
        self.assertEqual(verdict.unverified_issues, [])
        self.assertIn("no critic evaluations", verdict.summary)
