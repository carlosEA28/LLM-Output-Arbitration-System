import os
import unittest
from unittest.mock import patch

os.environ["LANGSMITH_TRACING"] = "false"

from src.arbitration.schemas.critique import CritiqueSchema, IssueSchema
from src.nodes import critics
from src.nodes.parse_input import parse_input


QUESTION = "What is the capital of France?"


class LogicCriticTests(unittest.TestCase):
    def run_critic(self, response, generated_output):
        class FakeGemini:
            def __init__(self, **kwargs):
                self.model = kwargs["model"]

            def with_structured_output(self, schema):
                self.test_case.assertIs(schema, CritiqueSchema)
                return self

            def invoke(self, messages):
                self.test_case.messages = messages
                return response

        FakeGemini.test_case = self
        with patch.object(critics, "ChatGoogleGenerativeAI", FakeGemini):
            state = parse_input({
                "original_question": f" {QUESTION} ",
                "generated_output": f" {generated_output} ",
            })
            return critics.logic_critic(state)

    def test_consistent_answer_is_evaluated_as_response(self):
        answer = "The capital of France is Berlin."
        response = CritiqueSchema(dimension="logic", score=5, confidence=0.5, issues=[])

        self.assertEqual(self.run_critic(response, answer), {"critiques": [response]})
        prompt = self.messages[1].content
        self.assertIn(f"**Original Question:**\n        {QUESTION}", prompt)
        self.assertIn(f"**Generated Response:**\n        {answer}", prompt)
        self.assertIn("Evaluate and quote only the generated response", self.messages[0].content)

    def test_contradictory_answer_keeps_issue_quote(self):
        answer = "The capital is Paris. The capital is Berlin."
        response = CritiqueSchema(
            dimension="logic", score=2, confidence=0.9,
            issues=[IssueSchema(
                quote="The capital is Berlin.",
                description="Contradicts the preceding sentence.", severity="high",
            )],
        )

        self.assertEqual(self.run_critic(response, answer), {"critiques": [response]})

    def test_question_quote_is_rejected(self):
        response = CritiqueSchema(
            dimension="logic", score=4, confidence=0.5,
            issues=[IssueSchema(quote=QUESTION, description="Wrong source.", severity="low")],
        )

        self.assertEqual(
            self.run_critic(response, "The capital of France is Berlin."),
            {"failed_critics": ["logic_critic"]},
        )

    def test_score_five_with_issues_is_rejected(self):
        response = CritiqueSchema(
            dimension="logic", score=5, confidence=0.5,
            issues=[IssueSchema(
                quote="The capital is Berlin.", description="Contradiction.", severity="low",
            )],
        )

        self.assertEqual(
            self.run_critic(response, "The capital is Berlin."),
            {"failed_critics": ["logic_critic"]},
        )


if __name__ == "__main__":
    unittest.main()
