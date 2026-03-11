from datetime import date, datetime

import pandas as pd
import yfinance as yf

from app.schemas.stock import HistoricalDataResponse, HistoricalPoint, StockSummary


class StockServiceError(Exception):
    """Domain-specific error for stock retrieval failures."""


class StockService:
    def __init__(self, tracked_symbols: list[str] | None = None) -> None:
        self.tracked_symbols = tracked_symbols or [
            "NVDA",
            "MSFT",
            "GOOGL",
            "AMD",
            "TSM",
            "AVGO",
            "AMZN",
            "META",
            "ASML",
        ]

    def list_symbols(self) -> list[str]:
        return self.tracked_symbols

    def get_stock_summary(self, symbol: str) -> StockSummary:
        validated_symbol = self._validate_symbol(symbol)
        ticker = yf.Ticker(validated_symbol)

        try:
            info = ticker.info or {}
        except Exception as exc:
            raise StockServiceError(f"Failed to load stock data for {validated_symbol}.") from exc

        return StockSummary(
            symbol=validated_symbol,
            company_name=info.get("longName"),
            sector=info.get("sector"),
            current_price=self._to_float(info.get("currentPrice")),
            market_cap=self._to_float(info.get("marketCap")),
            day_high=self._to_float(info.get("dayHigh")),
            day_low=self._to_float(info.get("dayLow")),
            currency=info.get("currency"),
            website=info.get("website"),
        )

    def get_historical_data(
        self,
        symbol: str,
        period: str = "3mo",
        interval: str = "1d",
    ) -> HistoricalDataResponse:
        validated_symbol = self._validate_symbol(symbol)
        ticker = yf.Ticker(validated_symbol)

        try:
            history = ticker.history(period=period, interval=interval, auto_adjust=False)
        except Exception as exc:
            raise StockServiceError(
                f"Failed to load historical data for {validated_symbol}."
            ) from exc

        if history.empty:
            raise StockServiceError(f"No historical data returned for {validated_symbol}.")

        prepared = self._normalize_history(history)
        points = [
            HistoricalPoint(
                date=row["date"],
                open=row["Open"],
                high=row["High"],
                low=row["Low"],
                close=row["Close"],
                volume=int(row["Volume"]),
            )
            for _, row in prepared.iterrows()
        ]
        return HistoricalDataResponse(symbol=validated_symbol, interval=interval, points=points)

    def _validate_symbol(self, symbol: str) -> str:
        normalized = symbol.strip().upper()
        if normalized not in self.tracked_symbols:
            available = ", ".join(self.tracked_symbols)
            raise StockServiceError(
                f"Ticker '{normalized}' is not tracked. Available: {available}"
            )
        return normalized

    @staticmethod
    def _normalize_history(frame: pd.DataFrame) -> pd.DataFrame:
        normalized = frame.copy()
        normalized = normalized.reset_index()
        if "Date" not in normalized.columns:
            normalized = normalized.rename(columns={normalized.columns[0]: "Date"})
        normalized["date"] = normalized["Date"].apply(StockService._coerce_date)
        normalized["Volume"] = normalized["Volume"].fillna(0).astype(int)
        normalized[["Open", "High", "Low", "Close"]] = normalized[
            ["Open", "High", "Low", "Close"]
        ].fillna(0.0)
        return normalized

    @staticmethod
    def _coerce_date(value: pd.Timestamp | datetime | date) -> date:
        if isinstance(value, pd.Timestamp):
            return value.date()
        if isinstance(value, datetime):
            return value.date()
        return value

    @staticmethod
    def _to_float(value: object) -> float | None:
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
