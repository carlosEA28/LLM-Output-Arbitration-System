from fastapi import APIRouter, HTTPException

from src.api.schemas.requests import EvaluationRequest, GenerationRequest
from src.api.schemas.responses import EvaluationResponse, GenerationEvaluationResponse
from src.api.services.arbitration_service import evaluate_response, generate_and_evaluate

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


@router.post("/generate-and-evaluate", response_model=GenerationEvaluationResponse)
def generate_and_evaluate_route(request: GenerationRequest) -> GenerationEvaluationResponse:
    try:
        result = generate_and_evaluate(request.original_question)
        return GenerationEvaluationResponse.model_validate(
            {**result, "adjudication": result.get("adjudication")}
        )
    except Exception:
        raise HTTPException(status_code=500, detail="Generation and evaluation failed") from None
