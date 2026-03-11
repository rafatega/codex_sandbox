from functools import lru_cache

from app.services.stock_service import StockService


@lru_cache
def get_stock_service() -> StockService:
    return StockService()
