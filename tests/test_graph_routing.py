import os
import unittest
from unittest.mock import patch

os.environ["LANGSMITH_TRACING"] = "false"

from src.arbitration import graph as graph_module


class GraphRoutingTests(unittest.TestCase):
    def run_path(self, requires_adjudication: bool) -> list[str]:
        with (
            patch.object(graph_module, "accuracy_critic", return_value={}),
            patch.object(graph_module, "logic_critic", return_value={}),
            patch.object(graph_module, "completeness_critic", return_value={}),
            patch.object(
                graph_module,
                "detect_disagreements",
                return_value={
                    "disagreements": ["conflict"] if requires_adjudication else [],
                    "requires_adjudication": requires_adjudication,
                },
            ),
        ):
            graph = graph_module.run_agents_graph()

        updates = graph.stream(
            {
                "original_question": "Question?",
                "generated_output": "Answer.",
                "critiques": [],
                "failed_critics": [],
            },
            stream_mode="updates",
        )
        return [node for update in updates for node in update]

    def test_adjudication_path(self):
        nodes = self.run_path(True)
        self.assertEqual(nodes[0], "parse_input")
        self.assertCountEqual(
            nodes[1:4],
            ["accuracy_critic", "logic_critic", "completeness_critic"],
        )
        self.assertEqual(
            nodes[4:],
            [
                "collect_critiques",
                "detect_disagreements",
                "adjudicator",
                "synthesize_verdict",
            ],
        )

    def test_direct_synthesis_path(self):
        nodes = self.run_path(False)
        self.assertEqual(nodes[0], "parse_input")
        self.assertCountEqual(
            nodes[1:4],
            ["accuracy_critic", "logic_critic", "completeness_critic"],
        )
        self.assertEqual(
            nodes[4:],
            [
                "collect_critiques",
                "detect_disagreements",
                "synthesize_verdict",
            ],
        )


if __name__ == "__main__":
    unittest.main()
