from fastapi import APIRouter

from app.config import get_settings
from app.ml.inference import inference_service
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", app=settings.app_name, model_mode=inference_service.classifier.__class__.__name__)

