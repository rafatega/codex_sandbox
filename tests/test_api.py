from fastapi.testclient import TestClient

from app.api.dependencies import get_stock_service
from app.main import app
from app.schemas.stock import HistoricalDataResponse, HistoricalPoint, StockSummary
from app.services.stock_service import StockServiceError


class FakeStockService:
    def list_symbols(self) -> list[str]:
        return ["NVDA", "MSFT"]

    def get_stock_summary(self, symbol: str) -> StockSummary:
        if symbol.upper() != "NVDA":
            raise StockServiceError("Ticker not tracked.")
        return StockSummary(
            symbol="NVDA",
            company_name="NVIDIA Corporation",
            sector="Technology",
            current_price=120.0,
            market_cap=10.0,
            day_high=121.0,
            day_low=119.0,
            currency="USD",
            website="https://www.nvidia.com",
        )

    def get_historical_data(
        self, symbol: str, period: str = "3mo", interval: str = "1d"
    ) -> HistoricalDataResponse:
        if symbol.upper() != "NVDA":
            raise StockServiceError("Ticker not tracked.")
        return HistoricalDataResponse(
            symbol="NVDA",
            interval=interval,
            points=[
                HistoricalPoint(
                    date="2026-01-01",
                    open=100.0,
                    high=110.0,
                    low=99.0,
                    close=108.0,
                    volume=1000,
                )
            ],
        )


def override_service() -> FakeStockService:
    return FakeStockService()


app.dependency_overrides[get_stock_service] = override_service
client = TestClient(app)


def test_healthcheck() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_stocks() -> None:
    response = client.get("/api/v1/stocks")
    assert response.status_code == 200
    assert response.json()["tracked_symbols"] == ["NVDA", "MSFT"]


def test_get_stock_success() -> None:
    response = client.get("/api/v1/stocks/NVDA")
    assert response.status_code == 200
    assert response.json()["symbol"] == "NVDA"


def test_get_stock_not_found() -> None:
    response = client.get("/api/v1/stocks/INVALID")
    assert response.status_code == 404


def test_get_stock_history_success() -> None:
    response = client.get("/api/v1/stocks/NVDA/history")
    assert response.status_code == 200
    assert len(response.json()["points"]) == 1


def test_get_stock_history_invalid_symbol() -> None:
    response = client.get("/api/v1/stocks/BAD/history")
    assert response.status_code == 400
