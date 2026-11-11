import httpx
from collections.abc import Callable
from uuid import UUID

from openai import APITimeoutError

from src.api import arbitration_history
from src.api.schemas.responses import EvaluationResponse, GenerationEvaluationResponse
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


def generate_and_evaluate(
    original_question: str, on_generated: Callable[[str], None] | None = None
) -> dict:
    generated_output = generate_response(original_question)
    if not generated_output.strip():
        raise ValueError("Generated response is blank")
    if on_generated is not None:
        on_generated(generated_output)
    result = evaluate_response(original_question, generated_output)
    return {**result, "generated_output": generated_output}


class PersistedExecutionError(Exception):
    def __init__(self, arbitration_id: UUID, *, timed_out: bool):
        self.arbitration_id = arbitration_id
        self.timed_out = timed_out


def generate_and_evaluate_persisted(original_question: str) -> GenerationEvaluationResponse:
    arbitration_id = arbitration_history.create(original_question)
    try:
        result = generate_and_evaluate(
            original_question,
            on_generated=lambda output: arbitration_history.save_generated_output(
                arbitration_id, output
            ),
        )
        evaluation = EvaluationResponse.model_validate(
            {**result, "adjudication": result.get("adjudication")}
        )
        response = GenerationEvaluationResponse.model_validate(
            {
                **evaluation.model_dump(),
                "id": arbitration_id,
                "generated_output": result["generated_output"],
            }
        )
        arbitration_history.complete(arbitration_id, evaluation)
        return response
    except Exception as error:
        timed_out = isinstance(
            error, (TimeoutError, httpx.TimeoutException, APITimeoutError)
        )
        try:
            arbitration_history.fail(arbitration_id, timed_out=timed_out)
        except Exception:
            timed_out = False
        raise PersistedExecutionError(arbitration_id, timed_out=timed_out) from None
