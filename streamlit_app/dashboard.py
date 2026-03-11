from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st

API_BASE_URL = "http://localhost:8000/api/v1"


@dataclass
class ApiClient:
    base_url: str
    timeout: int = 20

    def list_symbols(self) -> list[str]:
        response = requests.get(f"{self.base_url}/stocks", timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        return payload.get("tracked_symbols", [])

    def get_summary(self, symbol: str) -> dict:
        response = requests.get(f"{self.base_url}/stocks/{symbol}", timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def get_history(self, symbol: str, period: str, interval: str) -> pd.DataFrame:
        response = requests.get(
            f"{self.base_url}/stocks/{symbol}/history",
            params={"period": period, "interval": interval},
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        frame = pd.DataFrame(payload["points"])
        frame["date"] = pd.to_datetime(frame["date"])
        frame = frame.sort_values("date")
        frame["daily_return"] = frame["close"].pct_change() * 100
        frame["ma_20"] = frame["close"].rolling(window=20).mean()
        frame["ma_50"] = frame["close"].rolling(window=50).mean()
        return frame


@st.cache_data(ttl=300)
def load_symbols(client: ApiClient) -> list[str]:
    return client.list_symbols()


@st.cache_data(ttl=180)
def load_summary(client: ApiClient, symbol: str) -> dict:
    return client.get_summary(symbol)


@st.cache_data(ttl=180)
def load_history(client: ApiClient, symbol: str, period: str, interval: str) -> pd.DataFrame:
    return client.get_history(symbol=symbol, period=period, interval=interval)


def to_currency(value: float | None, currency: str | None) -> str:
    if value is None:
        return "N/A"
    prefix = "$" if currency == "USD" else ""
    return f"{prefix}{value:,.2f}"


def main() -> None:
    st.set_page_config(page_title="AI Tech Stocks Dashboard", layout="wide")
    st.title("AI Technology Stocks Dashboard")
    st.caption("Detailed analytics powered by FastAPI and yfinance.")

    with st.sidebar:
        st.header("Configuration")
        api_url = st.text_input("API base URL", value=API_BASE_URL)
        period = st.selectbox("Period", ["1mo", "3mo", "6mo", "1y", "2y", "5y"], index=1)
        interval = st.selectbox("Interval", ["1d", "1wk", "1mo"], index=0)

    client = ApiClient(base_url=api_url)
    try:
        symbols = load_symbols(client)
    except requests.RequestException as exc:
        st.error(f"Could not load symbols from API: {exc}")
        return

    if not symbols:
        st.warning("No symbols available from the API.")
        return

    selected_symbol = st.selectbox("Select stock ticker", symbols, index=0)
    try:
        summary = load_summary(client, selected_symbol)
        history = load_history(client, selected_symbol, period, interval)
    except requests.RequestException as exc:
        st.error(f"Could not load stock data from API: {exc}")
        return

    latest = history.iloc[-1]
    previous = history.iloc[-2] if len(history) > 1 else latest
    delta_pct = ((latest["close"] - previous["close"]) / previous["close"] * 100) if previous[
        "close"
    ] else 0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Price",
        to_currency(summary.get("current_price"), summary.get("currency")),
        f"{delta_pct:.2f}%",
    )
    col2.metric("Market Cap", to_currency(summary.get("market_cap"), summary.get("currency")))
    col3.metric("Day High", to_currency(summary.get("day_high"), summary.get("currency")))
    col4.metric("Day Low", to_currency(summary.get("day_low"), summary.get("currency")))

    company_name = summary.get("company_name") or selected_symbol
    sector = summary.get("sector") or "N/A"
    website = summary.get("website") or "N/A"
    st.subheader(f"{company_name} ({selected_symbol})")
    st.write(f"Sector: {sector}")
    st.write(f"Website: {website}")

    candlestick = go.Figure(
        data=[
            go.Candlestick(
                x=history["date"],
                open=history["open"],
                high=history["high"],
                low=history["low"],
                close=history["close"],
                name="Price",
            ),
            go.Scatter(x=history["date"], y=history["ma_20"], mode="lines", name="MA 20"),
            go.Scatter(x=history["date"], y=history["ma_50"], mode="lines", name="MA 50"),
        ]
    )
    candlestick.update_layout(
        title=f"{selected_symbol} Candlestick and Moving Averages",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False,
        height=550,
    )
    st.plotly_chart(candlestick, use_container_width=True)

    volume_chart = go.Figure()
    volume_chart.add_trace(
        go.Bar(
            x=history["date"],
            y=history["volume"],
            name="Volume",
        )
    )
    volume_chart.update_layout(
        title="Trading Volume",
        xaxis_title="Date",
        yaxis_title="Volume",
        height=350,
    )
    st.plotly_chart(volume_chart, use_container_width=True)

    return_chart = go.Figure()
    return_chart.add_trace(
        go.Scatter(
            x=history["date"],
            y=history["daily_return"],
            mode="lines",
            name="Daily Return %",
        )
    )
    return_chart.update_layout(
        title="Daily Return Variation (%)",
        xaxis_title="Date",
        yaxis_title="Return (%)",
        height=350,
    )
    st.plotly_chart(return_chart, use_container_width=True)

    st.subheader("Recent historical data")
    st.dataframe(
        history.sort_values("date", ascending=False).head(30),
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()
