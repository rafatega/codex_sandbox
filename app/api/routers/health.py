from fastapi import APIRouter

from app.schemas.stock import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse, summary="Healthcheck endpoint")
def healthcheck() -> HealthResponse:
    return HealthResponse()
