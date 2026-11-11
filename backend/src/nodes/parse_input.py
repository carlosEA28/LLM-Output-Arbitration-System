from src.arbitration.states import ArbitrationState


def parse_input(state: ArbitrationState) -> dict:
    generated_output = state.get("generated_output", "").strip()
    original_question = state.get("original_question", "").strip()

    if not generated_output:
        raise ValueError("Generated output is required")

    if not original_question:
        raise ValueError("Original question is required")

    return {
        "generated_output": generated_output,
        "original_question": original_question,
    }