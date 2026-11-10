from src.arbitration.graph import run_agents_graph


def evaluate_response(original_question: str, generated_output: str) -> dict:
    graph = run_agents_graph()
    return graph.invoke(
        {
            "original_question": original_question,
            "generated_output": generated_output,
            "critiques": [],
            "failed_critics": [],
        }
    )
