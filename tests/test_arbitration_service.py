from unittest.mock import Mock

from src.api.services import arbitration_service


def test_service_invokes_existing_graph_with_cli_input_state(monkeypatch):
    graph = Mock()
    graph.invoke.return_value = {"verdict": "controlled"}
    compile_graph = Mock(return_value=graph)
    monkeypatch.setattr(arbitration_service, "run_agents_graph", compile_graph)

    result = arbitration_service.evaluate_response("Question?", "Existing answer.")

    compile_graph.assert_called_once_with()
    graph.invoke.assert_called_once_with(
        {
            "original_question": "Question?",
            "generated_output": "Existing answer.",
            "critiques": [],
            "failed_critics": [],
        }
    )
    assert result is graph.invoke.return_value
