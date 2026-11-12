from fastapi import APIRouter, HTTPException

from src.api.schemas.responses import AnalyticsResponse
from src.api.services.analytics_service import get_analytics

router = APIRouter()


@router.get("/v1/analytics", response_model=AnalyticsResponse)
def analytics() -> AnalyticsResponse:
    try:
        return AnalyticsResponse.model_validate(get_analytics())
    except Exception:
        raise HTTPException(status_code=500, detail="Analytics retrieval failed") from None
