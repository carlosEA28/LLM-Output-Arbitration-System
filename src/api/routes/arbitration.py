from fastapi import APIRouter, HTTPException

from src.api.schemas.requests import EvaluationRequest
from src.api.schemas.responses import EvaluationResponse
from src.api.services.arbitration_service import evaluate_response

router = APIRouter()


@router.post("/evaluate", response_model=EvaluationResponse)
def evaluate(request: EvaluationRequest) -> EvaluationResponse:
    try:
        result = evaluate_response(request.original_question, request.generated_output)
        return EvaluationResponse.model_validate(
            {**result, "adjudication": result.get("adjudication")}
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Evaluation failed") from None
