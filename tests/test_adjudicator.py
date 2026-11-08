import unittest
from unittest.mock import Mock, patch

from src.arbitration.schemas.critique import CritiqueSchema, IssueSchema
from src.arbitration.schemas.verdict import AdjudicationSchema, DismissedIssueSchema
from src.nodes import adjudicator as node


class AdjudicatorTests(unittest.TestCase):
    def setUp(self):
        self.issue = IssueSchema(description="Claim is false", severity="high")
        self.other = IssueSchema(description="Missing context", severity="medium")
        self.state = {
            "original_question": "Question?", "generated_output": "Answer.",
            "critiques": [CritiqueSchema(dimension="accuracy", score=2, confidence=0.7, issues=[self.issue, self.other])],
            "disagreements": ["accuracy vs logic: conflict"],
        }

    def invoke(self, result):
        model = Mock()
        model.with_structured_output.return_value = model
        model.invoke.return_value = result
        with patch.object(node, "ChatOpenAI", return_value=model):
            update = node.adjudicator(self.state)
        model.with_structured_output.assert_called_once_with(AdjudicationSchema)
        messages = model.invoke.call_args.args[0]
        self.assertIn("Question?", messages[1].content)
        self.assertIn("Answer.", messages[1].content)
        self.assertIn("Claim is false", messages[1].content)
        self.assertIn("conflict", messages[1].content)
        return update

    def test_grounded_confirmation_and_dismissal(self):
        result = AdjudicationSchema(confirmed_issues=[self.issue], dismissed_issues=[
            DismissedIssueSchema(issue=self.other, reason="The response covers it")
        ])
        self.assertIs(self.invoke(result)["adjudication"], result)

    def test_unmentioned_issue_is_allowed(self):
        self.assertEqual(self.invoke(AdjudicationSchema())["adjudication"].confirmed_issues, [])

    def test_rejects_invented_or_contradictory_decisions(self):
        invented = IssueSchema(description="Invented", severity="low")
        for result in (
            AdjudicationSchema(confirmed_issues=[invented]),
            AdjudicationSchema(confirmed_issues=[self.issue], dismissed_issues=[
                DismissedIssueSchema(issue=self.issue, reason="No basis")
            ]),
        ):
            with self.subTest(result=result), self.assertRaises(ValueError):
                self.invoke(result)
