from fastapi import FastAPI

from app.api.routers.health import router as health_router
from app.api.routers.stocks import router as stocks_router
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="RESTful API for AI-related technology stock market data.",
)

app.include_router(health_router, prefix=settings.api_prefix)
app.include_router(stocks_router, prefix=settings.api_prefix)
