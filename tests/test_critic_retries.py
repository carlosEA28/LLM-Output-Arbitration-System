import os
import unittest
from unittest.mock import Mock, patch

import httpx
from google.genai.errors import ClientError
from langchain_google_genai.chat_models import GoogleRateLimitError

os.environ["LANGSMITH_TRACING"] = "false"

from src.arbitration import graph as graph_module
from src.arbitration.schemas.critique import CritiqueSchema
from src.nodes import critics


INPUT = {
    "original_question": "Question?",
    "generated_output": "Answer.",
}

CRITICS = (
    (critics.accuracy_critic, "ChatOpenAI", "accuracy"),
    (critics.logic_critic, "ChatGoogleGenerativeAI", "logic"),
    (critics.completeness_critic, "ChatOpenAI", "completeness"),
)


class CriticRetriesTests(unittest.TestCase):
    def test_each_critic_retries_a_transient_model_failure(self):
        for critic, client_name, dimension in CRITICS:
            with self.subTest(dimension=dimension):
                critique = CritiqueSchema(dimension=dimension, score=5, confidence=1.0)
                model = Mock()
                model.with_structured_output.return_value = model
                failure = (ClientError(429, {"message": "secret rate limit"})
                           if dimension == "logic" else httpx.ReadTimeout("secret timeout"))
                model.invoke.side_effect = [failure, critique]

                with patch.object(critics, client_name, return_value=model) as client, patch.object(critics.time, "sleep") as sleep:
                    result = critic(INPUT)

                self.assertEqual(result, {"critiques": [critique]})
                self.assertEqual(model.invoke.call_count, critics.MAX_LLM_ATTEMPTS)
                sleep.assert_called_once_with(1)
                self.assertEqual(client.call_args.kwargs["retries" if dimension == "logic" else "max_retries"],
                                 1 if dimension == "logic" else 0)

    def test_each_critic_records_failure_after_retry_limit(self):
        for critic, client_name, dimension in CRITICS:
            with self.subTest(dimension=dimension):
                model = Mock()
                model.with_structured_output.return_value = model
                model.invoke.side_effect = httpx.ConnectError("secret connection")

                with patch.object(critics, client_name, return_value=model), patch.object(critics.time, "sleep") as sleep:
                    with self.assertLogs(critics.logger, level="WARNING") as logs:
                        result = critic(INPUT)

                self.assertEqual(result, {"failed_critics": [f"{dimension}_critic"]})
                self.assertEqual(model.invoke.call_count, critics.MAX_LLM_ATTEMPTS)
                sleep.assert_called_once_with(1)
                self.assertIn("category=connection", logs.output[0])
                self.assertNotIn("secret", logs.output[0])

    def test_authentication_and_generic_errors_do_not_retry(self):
        for failure, category in (
            (ClientError(401, {"message": "secret credential"}), "authentication"),
            (RuntimeError("secret generic failure"), "call_error"),
        ):
            with self.subTest(category=category):
                model = Mock()
                model.with_structured_output.return_value = model
                model.invoke.side_effect = failure
                with patch.object(critics, "ChatGoogleGenerativeAI", return_value=model), patch.object(critics.time, "sleep") as sleep:
                    with self.assertLogs(critics.logger, level="WARNING") as logs:
                        result = critics.logic_critic(INPUT)
                self.assertEqual(result, {"failed_critics": ["logic_critic"]})
                self.assertEqual(model.invoke.call_count, 1)
                sleep.assert_not_called()
                self.assertIn(f"category={category}", logs.output[0])
                self.assertNotIn("secret", logs.output[0])

    def test_google_wrapped_rate_limit_retries(self):
        critique = CritiqueSchema(dimension="logic", score=5, confidence=1.0)
        failure = GoogleRateLimitError("secret wrapper")
        failure.__cause__ = ClientError(429, {"message": "secret API detail"})
        model = Mock()
        model.with_structured_output.return_value = model
        model.invoke.side_effect = [failure, critique]
        with patch.object(critics, "ChatGoogleGenerativeAI", return_value=model), patch.object(critics.time, "sleep") as sleep:
            result = critics.logic_critic(INPUT)
        self.assertEqual(result, {"critiques": [critique]})
        self.assertEqual(model.invoke.call_count, 2)
        sleep.assert_called_once_with(1)

    def test_graph_finishes_with_all_critics_failed(self):
        with (
            patch.object(graph_module, "accuracy_critic", return_value={"failed_critics": ["accuracy_critic"]}),
            patch.object(graph_module, "logic_critic", return_value={"failed_critics": ["logic_critic"]}),
            patch.object(graph_module, "completeness_critic", return_value={"failed_critics": ["completeness_critic"]}),
        ):
            graph = graph_module.run_agents_graph()

        result = graph.invoke({**INPUT, "critiques": [], "failed_critics": [], "verdict": None})

        self.assertEqual(result["critiques"], [])
        self.assertCountEqual(
            result["failed_critics"],
            ["accuracy_critic", "logic_critic", "completeness_critic"],
        )
        self.assertEqual(result["missing_dimensions"], ["accuracy", "logic", "completeness"])
        self.assertEqual(result["duplicate_dimensions"], [])
        self.assertFalse(result["critiques_complete"])
        self.assertEqual(result["disagreements"], [])
        self.assertFalse(result["requires_adjudication"])
        self.assertIsNone(result["verdict"])


if __name__ == "__main__":
    unittest.main()
