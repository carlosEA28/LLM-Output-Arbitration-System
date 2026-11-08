import os
import unittest
from unittest.mock import patch

os.environ["LANGSMITH_TRACING"] = "false"

from src.arbitration.schemas.critique import CritiqueSchema
from src.nodes.collect_critiques import collect_critiques


def critique(dimension: str) -> CritiqueSchema:
    return CritiqueSchema(dimension=dimension, score=5, confidence=1.0)


class CollectCritiquesTests(unittest.TestCase):
    def test_complete_set(self):
        state = {
            "critiques": [critique("accuracy"), critique("logic"), critique("completeness")],
            "failed_critics": [],
        }

        self.assertEqual(
            collect_critiques(state),
            {
                "missing_dimensions": [],
                "duplicate_dimensions": [],
                "critiques_complete": True,
            },
        )

    def test_empty_critiques(self):
        result = collect_critiques({"critiques": [], "failed_critics": []})
        self.assertEqual(result["missing_dimensions"], ["accuracy", "logic", "completeness"])
        self.assertFalse(result["critiques_complete"])

    def test_missing_duplicate_and_failed(self):
        state = {
            "critiques": [critique("accuracy"), critique("accuracy"), critique("completeness")],
            "failed_critics": ["logic_critic"],
        }

        result = collect_critiques(state)
        self.assertEqual(result["missing_dimensions"], ["logic"])
        self.assertEqual(result["duplicate_dimensions"], ["accuracy"])
        self.assertFalse(result["critiques_complete"])

    def test_recorded_failure_makes_collection_incomplete(self):
        state = {
            "critiques": [critique("accuracy"), critique("logic"), critique("completeness")],
            "failed_critics": ["logic_critic"],
        }
        self.assertFalse(collect_critiques(state)["critiques_complete"])

    def test_graph_collects_after_critic_failure(self):
        from src.arbitration import graph as graph_module

        with (
            patch.object(graph_module, "accuracy_critic", return_value={"critiques": [critique("accuracy")]}),
            patch.object(graph_module, "logic_critic", return_value={"failed_critics": ["logic_critic"]}),
            patch.object(graph_module, "completeness_critic", return_value={"critiques": [critique("completeness")]}),
        ):
            graph = graph_module.run_agents_graph()

        result = graph.invoke({
            "original_question": "Question?",
            "generated_output": "Answer.",
            "critiques": [],
            "failed_critics": [],
        })

        self.assertEqual(result["missing_dimensions"], ["logic"])
        self.assertEqual(result["duplicate_dimensions"], [])
        self.assertEqual(result["failed_critics"], ["logic_critic"])
        self.assertFalse(result["critiques_complete"])
        self.assertCountEqual(
            [item.dimension.value for item in result["critiques"]],
            ["accuracy", "completeness"],
        )
        self.assertIsNone(result.get("verdict"))

    def test_graph_preserves_three_critiques(self):
        from src.arbitration import graph as graph_module

        with (
            patch.object(graph_module, "accuracy_critic", return_value={"critiques": [critique("accuracy")]}),
            patch.object(graph_module, "logic_critic", return_value={"critiques": [critique("logic")]}),
            patch.object(graph_module, "completeness_critic", return_value={"critiques": [critique("completeness")]}),
        ):
            graph = graph_module.run_agents_graph()

        result = graph.invoke({
            "original_question": "Question?",
            "generated_output": "Answer.",
            "critiques": [],
            "failed_critics": [],
        })

        self.assertTrue(result["critiques_complete"])
        self.assertCountEqual(
            [item.dimension.value for item in result["critiques"]],
            ["accuracy", "logic", "completeness"],
        )
        self.assertEqual(result["failed_critics"], [])
        self.assertEqual(result["missing_dimensions"], [])
        self.assertEqual(result["duplicate_dimensions"], [])

    def test_logic_critic_records_model_failure(self):
        from src.nodes import critics

        with patch.object(critics, "ChatGoogleGenerativeAI", side_effect=RuntimeError("model unavailable")):
            result = critics.logic_critic({
                "original_question": "Question?",
                "generated_output": "Answer.",
            })

        self.assertEqual(result, {"failed_critics": ["logic_critic"]})


if __name__ == "__main__":
    unittest.main()
