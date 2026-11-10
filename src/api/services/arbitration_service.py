from src.arbitration.graph import run_agents_graph
from src.arbitration.main import generate_response


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


def generate_and_evaluate(original_question: str) -> dict:
    generated_output = generate_response(original_question)
    if not generated_output.strip():
        raise ValueError("Generated response is blank")
    result = evaluate_response(original_question, generated_output)
    return {**result, "generated_output": generated_output}
