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


def test_generate_and_evaluate_passes_exact_answer_to_existing_service(monkeypatch):
    calls = []

    def generate(question):
        calls.append(("generate", question))
        return " Generated answer. "

    def evaluate(question, answer):
        calls.append(("evaluate", question, answer))
        return {"verdict": "controlled"}

    monkeypatch.setattr(arbitration_service, "generate_response", generate)
    monkeypatch.setattr(arbitration_service, "evaluate_response", evaluate)

    result = arbitration_service.generate_and_evaluate("Question?")

    assert calls == [
        ("generate", "Question?"),
        ("evaluate", "Question?", " Generated answer. "),
    ]
    assert result == {
        "verdict": "controlled",
        "generated_output": " Generated answer. ",
    }


def test_generate_and_evaluate_rejects_blank_answer_without_graph(monkeypatch):
    generator = Mock(return_value=" \t ")
    evaluation = Mock()
    monkeypatch.setattr(arbitration_service, "generate_response", generator)
    monkeypatch.setattr(arbitration_service, "evaluate_response", evaluation)

    try:
        arbitration_service.generate_and_evaluate("Question?")
    except ValueError:
        pass
    else:
        raise AssertionError("Blank generation must fail")

    generator.assert_called_once_with("Question?")
    evaluation.assert_not_called()
