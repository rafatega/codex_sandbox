from datetime import date

from pydantic import BaseModel, Field


class StockSummary(BaseModel):
    symbol: str = Field(..., examples=["NVDA"])
    company_name: str | None = Field(default=None, examples=["NVIDIA Corporation"])
    sector: str | None = Field(default=None, examples=["Technology"])
    current_price: float | None = Field(default=None, examples=[123.45])
    market_cap: float | None = Field(default=None, examples=[3_000_000_000_000])
    day_high: float | None = Field(default=None, examples=[125.50])
    day_low: float | None = Field(default=None, examples=[121.30])
    currency: str | None = Field(default=None, examples=["USD"])
    website: str | None = Field(default=None, examples=["https://www.nvidia.com"])


class HistoricalPoint(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int


class HistoricalDataResponse(BaseModel):
    symbol: str
    interval: str
    points: list[HistoricalPoint]


class StockListResponse(BaseModel):
    tracked_symbols: list[str]


class HealthResponse(BaseModel):
    status: str = "ok"
