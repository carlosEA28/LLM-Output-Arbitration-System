from unittest.mock import Mock

from src.arbitration import main as cli


def test_shared_generator_preserves_cli_model_and_text_conversion(monkeypatch):
    model = Mock()
    model.invoke.return_value.content = "Generated answer."
    constructor = Mock(return_value=model)
    monkeypatch.setattr(cli, "ChatOpenAI", constructor)

    assert cli.generate_response("Question?") == "Generated answer."

    constructor.assert_called_once_with(model="gpt-5-mini")
    model.invoke.assert_called_once_with("Question?")


def test_cli_still_passes_generated_answer_to_graph(monkeypatch):
    graph = Mock()
    graph.invoke.return_value = {"critiques": [], "verdict": None}
    generator = Mock(return_value="Generated answer.")
    monkeypatch.setattr("builtins.input", lambda _: "  Question?  ")
    monkeypatch.setattr(cli, "generate_response", generator)
    monkeypatch.setattr(cli, "run_agents_graph", Mock(return_value=graph))

    cli.main()

    generator.assert_called_once_with("Question?")
    graph.invoke.assert_called_once_with(
        {
            "original_question": "Question?",
            "generated_output": "Generated answer.",
            "critiques": [],
            "failed_critics": [],
        }
    )
