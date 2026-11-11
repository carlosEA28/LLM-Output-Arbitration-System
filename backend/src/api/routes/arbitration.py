import httpx
from uuid import UUID

from fastapi import APIRouter, HTTPException, Response
from openai import APITimeoutError

from src.api import arbitration_history
from src.api.schemas.requests import BatchEvaluationRequest, EvaluationRequest, GenerationRequest
from src.api.schemas.responses import (
    ArbitrationHistoryResponse,
    BatchEvaluationItemResponse,
    BatchEvaluationResponse,
    EvaluationResponse,
    GenerationEvaluationResponse,
)
from src.api.services.arbitration_service import (
    PersistedExecutionError,
    evaluate_response,
    generate_and_evaluate_persisted,
)

router = APIRouter()


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    try:
        result = evaluate_response(request.original_question, request.generated_output)
        return EvaluationResponse.model_validate(
            {**result, "adjudication": result.get("adjudication")}
        )
    except (TimeoutError, httpx.TimeoutException, APITimeoutError):
        raise HTTPException(status_code=504, detail="Evaluation timed out") from None
    except Exception:
        raise HTTPException(status_code=500, detail="Evaluation failed") from None


@router.post("/v1/arbitrate/batch", response_model=BatchEvaluationResponse)
def evaluate_batch(request: BatchEvaluationRequest) -> BatchEvaluationResponse:
    results = []
    for index, item in enumerate(request.items):
        try:
            result = evaluate_response(item.original_question, item.generated_output)
            evaluation = EvaluationResponse.model_validate(
                {**result, "adjudication": result.get("adjudication")}
            )
            results.append(BatchEvaluationItemResponse(
                index=index, status="completed", evaluation=evaluation, error=None
            ))
        except (TimeoutError, httpx.TimeoutException, APITimeoutError):
            results.append(BatchEvaluationItemResponse(
                index=index, status="timed_out", evaluation=None,
                error="Evaluation timed out",
            ))
        except Exception:
            results.append(BatchEvaluationItemResponse(
                index=index, status="failed", evaluation=None,
                error="Evaluation failed",
            ))
    return BatchEvaluationResponse(results=results)


@router.post("/generate-and-evaluate", response_model=GenerationEvaluationResponse)
def generate_and_evaluate_route(
    request: GenerationRequest, response: Response
) -> GenerationEvaluationResponse:
    try:
        result = generate_and_evaluate_persisted(request.original_question)
        response.headers["X-Arbitration-ID"] = str(result.id)
        return result
    except PersistedExecutionError as error:
        status_code = 504 if error.timed_out else 500
        detail = (
            "Generation and evaluation timed out"
            if error.timed_out else "Generation and evaluation failed"
        )
        raise HTTPException(
            status_code=status_code,
            detail=detail,
            headers={"X-Arbitration-ID": str(error.arbitration_id)},
        ) from None
    except Exception:
        raise HTTPException(status_code=500, detail="Generation and evaluation failed") from None


@router.get("/v1/arbitrations/{id}", response_model=ArbitrationHistoryResponse)
def get_arbitration(id: UUID) -> ArbitrationHistoryResponse:
    try:
        record = arbitration_history.get(id)
        if record is None:
            raise HTTPException(status_code=404, detail="Arbitration not found")
        return ArbitrationHistoryResponse.model_validate(record)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="History retrieval failed") from None
