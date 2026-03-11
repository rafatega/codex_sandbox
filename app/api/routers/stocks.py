from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_stock_service
from app.schemas.stock import HistoricalDataResponse, StockListResponse, StockSummary
from app.services.stock_service import StockService, StockServiceError

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get(
    "",
    response_model=StockListResponse,
    summary="List tracked AI-related technology stock symbols",
)
def list_stocks(service: StockService = Depends(get_stock_service)) -> StockListResponse:
    return StockListResponse(tracked_symbols=service.list_symbols())


@router.get(
    "/{symbol}",
    response_model=StockSummary,
    summary="Get summary data for a tracked stock symbol",
)
def get_stock(symbol: str, service: StockService = Depends(get_stock_service)) -> StockSummary:
    try:
        return service.get_stock_summary(symbol)
    except StockServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.get(
    "/{symbol}/history",
    response_model=HistoricalDataResponse,
    summary="Get historical OHLCV data for a tracked stock symbol",
)
def get_stock_history(
    symbol: str,
    period: str = Query(
        default="3mo",
        description="Valid yfinance period, for example: 1mo, 3mo, 6mo, 1y, 2y, 5y",
    ),
    interval: str = Query(
        default="1d",
        description="Valid yfinance interval, for example: 1d, 1wk, 1mo",
    ),
    service: StockService = Depends(get_stock_service),
) -> HistoricalDataResponse:
    try:
        return service.get_historical_data(symbol=symbol, period=period, interval=interval)
    except StockServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
