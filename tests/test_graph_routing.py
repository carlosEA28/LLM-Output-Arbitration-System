import os
import unittest
from unittest.mock import Mock, patch

os.environ["LANGSMITH_TRACING"] = "false"

from src.arbitration import graph as graph_module
from src.arbitration.schemas.critique import CritiqueSchema, IssueSchema
from src.arbitration.schemas.disagreement import ConflictAssessment, IssueConflict
from src.arbitration.schemas.verdict import AdjudicationSchema, VerdictSchema
from src.nodes import detect_disagreements as detector
from src.nodes import adjudicator as adjudicator_node


class GraphRoutingTests(unittest.TestCase):
    def test_incomplete_evaluations_preserve_critical_issue_without_adjudication(self):
        critical = IssueSchema(description="The claim is false.", severity="critical")
        accuracy = CritiqueSchema(dimension="accuracy", score=1, confidence=0.9, issues=[critical])
        completeness = CritiqueSchema(dimension="completeness", score=5, confidence=0.9)
        with (
            patch.object(graph_module, "accuracy_critic", return_value={"critiques": [accuracy]}),
            patch.object(graph_module, "logic_critic", return_value={"failed_critics": ["logic_critic"]}),
            patch.object(graph_module, "completeness_critic", return_value={"critiques": [completeness]}),
            patch.object(detector, "ChatOpenAI") as model,
        ):
            graph = graph_module.run_agents_graph()
            updates = list(graph.stream({
                "original_question": "Question?", "generated_output": "Answer.",
                "critiques": [], "failed_critics": [], "verdict": None,
            }, stream_mode="updates"))
            result = graph.invoke({
                "original_question": "Question?", "generated_output": "Answer.",
                "critiques": [], "failed_critics": [], "verdict": None,
            })

        node_updates = {node: value for update in updates for node, value in update.items()}
        nodes = [node for update in updates for node in update]
        self.assertCountEqual(nodes[1:4], ["accuracy_critic", "logic_critic", "completeness_critic"])
        self.assertEqual(nodes[5:], [
            "detect_disagreements", "synthesize_verdict",
        ])
        self.assertEqual(node_updates["collect_critiques"]["missing_dimensions"], ["logic"])
        self.assertFalse(node_updates["collect_critiques"]["critiques_complete"])
        self.assertFalse(node_updates["detect_disagreements"]["requires_adjudication"])
        self.assertCountEqual(
            [item.dimension.value for item in result["critiques"]],
            ["accuracy", "completeness"],
        )
        retained_accuracy = next(item for item in result["critiques"] if item.dimension.value == "accuracy")
        self.assertEqual(retained_accuracy.issues[0].severity.value, "critical")
        self.assertIsInstance(result["verdict"], VerdictSchema)
        self.assertEqual(result["verdict"].confirmed_issues, [])
        self.assertEqual(result["verdict"].unverified_issues, [critical])
        self.assertEqual(result["verdict"].confidence, 0.5)
        model.assert_not_called()

    def test_available_conflicting_issues_route_to_adjudicator(self):
        accuracy = CritiqueSchema(dimension="accuracy", score=1, confidence=0.9, issues=[
            IssueSchema(description="The claim is false.", severity="high"),
        ])
        logic = CritiqueSchema(dimension="logic", score=2, confidence=0.9, issues=[
            IssueSchema(description="The same claim is true.", severity="high"),
        ])
        model = Mock()
        model.with_structured_output.return_value = model
        model.invoke.return_value = ConflictAssessment(conflicts=[IssueConflict(
            first_issue=0, second_issue=1, explanation="Opposite assessments of the same claim.",
        )])
        adjudicator_model = Mock()
        adjudicator_model.with_structured_output.return_value = adjudicator_model
        adjudicator_model.invoke.return_value = AdjudicationSchema(
            confirmed_issues=accuracy.issues,
            dismissed_issues=[],
        )
        with (
            patch.object(graph_module, "accuracy_critic", return_value={"critiques": [accuracy]}),
            patch.object(graph_module, "logic_critic", return_value={"critiques": [logic]}),
            patch.object(graph_module, "completeness_critic", return_value={"failed_critics": ["completeness_critic"]}),
            patch.object(detector, "ChatOpenAI", return_value=model),
            patch.object(adjudicator_node, "ChatOpenAI", return_value=adjudicator_model),
        ):
            graph = graph_module.run_agents_graph()
            updates = list(graph.stream({
                "original_question": "Question?", "generated_output": "Answer.",
                "critiques": [], "failed_critics": [], "verdict": None,
            }, stream_mode="updates"))

        node_updates = {node: value for update in updates for node, value in update.items()}
        nodes = [node for update in updates for node in update]
        self.assertCountEqual(nodes[1:4], ["accuracy_critic", "logic_critic", "completeness_critic"])
        self.assertEqual(nodes[5:], [
            "detect_disagreements", "adjudicator", "synthesize_verdict",
        ])
        self.assertEqual(node_updates["collect_critiques"]["missing_dimensions"], ["completeness"])
        self.assertFalse(node_updates["collect_critiques"]["critiques_complete"])
        self.assertTrue(node_updates["detect_disagreements"]["requires_adjudication"])
        self.assertEqual(len(node_updates["detect_disagreements"]["disagreements"]), 1)
        model.invoke.assert_called_once()
        adjudicator_model.invoke.assert_called_once()
        self.assertEqual(node_updates["synthesize_verdict"]["verdict"].status, "assessed")
        self.assertIn(accuracy.issues[0], node_updates["synthesize_verdict"]["verdict"].confirmed_issues)

    def run_path(self, requires_adjudication: bool) -> list[str]:
        with (
            patch.object(graph_module, "accuracy_critic", return_value={}),
            patch.object(graph_module, "logic_critic", return_value={}),
            patch.object(graph_module, "completeness_critic", return_value={}),
            patch.object(graph_module, "adjudicator", return_value={"adjudication": AdjudicationSchema()}),
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

    def test_all_critics_failed_reaches_inconclusive_verdict(self):
        with (
            patch.object(graph_module, "accuracy_critic", return_value={"failed_critics": ["accuracy_critic"]}),
            patch.object(graph_module, "logic_critic", return_value={"failed_critics": ["logic_critic"]}),
            patch.object(graph_module, "completeness_critic", return_value={"failed_critics": ["completeness_critic"]}),
        ):
            graph = graph_module.run_agents_graph()
        result = graph.invoke({"original_question": "Question?", "generated_output": "Answer.", "critiques": [], "failed_critics": []})
        self.assertEqual(result["verdict"].status, "inconclusive")
        self.assertEqual(result["verdict"].confidence, 0)


if __name__ == "__main__":
    unittest.main()
