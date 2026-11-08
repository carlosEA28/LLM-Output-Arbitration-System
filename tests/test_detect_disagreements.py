import os
import unittest
from unittest.mock import patch

os.environ["LANGSMITH_TRACING"] = "false"

from src.arbitration.schemas.critique import CritiqueSchema, IssueSchema
from src.arbitration.schemas.disagreement import ConflictAssessment, IssueConflict
from src.nodes import detect_disagreements as detector


def critique(dimension, score, *descriptions):
    return CritiqueSchema(
        dimension=dimension,
        score=score,
        confidence=0.9,
        issues=[IssueSchema(description=text, severity="high") for text in descriptions],
    )


class FakeModel:
    def __init__(self, assessment):
        self.assessment = assessment
        self.messages = None

    def with_structured_output(self, schema):
        assert schema is ConflictAssessment
        return self

    def invoke(self, messages):
        self.messages = messages
        return self.assessment


class DetectDisagreementsTests(unittest.TestCase):
    def test_opposite_scores_in_different_dimensions_are_not_conflict(self):
        state = {"critiques": [
            critique("accuracy", 1, "Berlin is not the capital of France."),
            critique("completeness", 5),
        ]}
        with patch.object(detector, "ChatOpenAI") as model:
            result = detector.detect_disagreements(state)
        self.assertEqual(result, {"disagreements": [], "requires_adjudication": False})
        model.assert_not_called()

    def test_explicit_contradiction_requires_adjudication(self):
        state = {
            "original_question": "What is the capital of France?",
            "generated_output": "Berlin is the capital of France.",
            "critiques": [
                critique("accuracy", 1, "The answer says Berlin, which is factually false."),
                critique("logic", 2, "The answer's claim that Berlin is the capital is factually true."),
            ],
        }
        fake = FakeModel(ConflictAssessment(conflicts=[
            IssueConflict(
                first_issue=0, second_issue=1,
                explanation="The same capital claim cannot be both true and false.",
            ),
        ]))
        with patch.object(detector, "ChatOpenAI", return_value=fake):
            result = detector.detect_disagreements(state)
        self.assertTrue(result["requires_adjudication"])
        self.assertEqual(len(result["disagreements"]), 1)
        self.assertIn("accuracy (issue 1) vs logic (issue 1)", result["disagreements"][0])
        self.assertIn("Berlin", fake.messages[1].content)

    def test_compatible_issues_do_not_require_adjudication(self):
        state = {"critiques": [
            critique("accuracy", 1, "Berlin is factually incorrect."),
            critique("completeness", 3, "The response omits the requested population."),
        ]}
        fake = FakeModel(ConflictAssessment())
        with patch.object(detector, "ChatOpenAI", return_value=fake):
            result = detector.detect_disagreements(state)
        self.assertEqual(result, {"disagreements": [], "requires_adjudication": False})

    def test_invalid_and_duplicate_model_references_are_ignored(self):
        state = {"critiques": [
            critique("accuracy", 1, "Claim is false.", "Citation is fabricated."),
            critique("logic", 2, "Claim is true."),
        ]}
        fake = FakeModel(ConflictAssessment(conflicts=[
            IssueConflict(first_issue=0, second_issue=1, explanation="Same critic."),
            IssueConflict(first_issue=0, second_issue=9, explanation="Missing issue."),
            IssueConflict(first_issue=0, second_issue=2, explanation="Conflicting claims."),
            IssueConflict(first_issue=2, second_issue=0, explanation="Repeated."),
        ]))
        with patch.object(detector, "ChatOpenAI", return_value=fake):
            result = detector.detect_disagreements(state)
        self.assertEqual(len(result["disagreements"]), 1)
        self.assertTrue(result["requires_adjudication"])


if __name__ == "__main__":
    unittest.main()
