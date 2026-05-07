import requests
from utils import normalize_symbol

from config import ALPHA_VANTAGE_API_KEY


class AlphaVantageProvider:
    name = "alpha_vantage"
    base_url = "https://www.alphavantage.co/query"

    def __init__(self, api_key=None):
        self.api_key = api_key if api_key is not None else ALPHA_VANTAGE_API_KEY

    def enabled(self):
        return bool(self.api_key)

    def quote(self, symbol):
        self._require_key()
        payload = self._request({"function": "GLOBAL_QUOTE", "symbol": symbol})
        quote = payload.get("Global Quote") or {}
        if not quote:
            raise ValueError("Alpha Vantage returned no quote data")

        return {
            "symbol": symbol.upper(),
            "name": symbol.upper(),
            "price": _float(quote.get("05. price")),
            "currency": "USD",
            "change": _float(quote.get("09. change")),
            "changePercent": _percent(quote.get("10. change percent")),
            "volume": int(float(quote.get("06. volume") or 0)),
            "marketCap": None,
            "provider": self.name,
        }

    def history(self, symbol, range_key="1mo"):
        self._require_key()
        payload = self._request({
            "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": symbol,
            "outputsize": "compact",
        })
        series = payload.get("Time Series (Daily)") or {}
        if not series:
            raise ValueError("Alpha Vantage returned no historical data")

        days = {"10d": 10, "1mo": 22, "3mo": 66, "6mo": 132, "1y": 252}.get(range_key, 22)
        rows = []
        for date in sorted(series.keys())[-days:]:
            row = series[date]
            rows.append({
                "date": date,
                "open": _float(row.get("1. open")),
                "high": _float(row.get("2. high")),
                "low": _float(row.get("3. low")),
                "close": _float(row.get("4. close")),
                "volume": int(float(row.get("6. volume") or 0)),
            })
        return rows

    def search(self, query):
        self._require_key()
        payload = self._request({"function": "SYMBOL_SEARCH", "keywords": query})
        matches = payload.get("bestMatches") or []
        return [{
            "symbol": item.get("1. symbol"),
            "name": item.get("2. name"),
            "exchange": item.get("4. region"),
            "provider": self.name,
        } for item in matches[:8]]

    def news(self, symbol=None, category="general"):
        self._require_key()
        params = {
            "function": "NEWS_SENTIMENT",
            "limit": 20,
            "sort": "LATEST",
        }
        if symbol:
            params["tickers"] = normalize_symbol(symbol)
        elif category and category != "general":
            params["topics"] = category

        payload = self._request(params)
        feed = payload.get("feed") or []
        if not isinstance(feed, list):
            raise ValueError("Alpha Vantage returned no news feed")
        return feed[:20]

    def _request(self, params):
        response = requests.get(
            self.base_url,
            params={**params, "apikey": self.api_key},
            timeout=12,
        )
        response.raise_for_status()
        payload = response.json()
        if "Note" in payload or "Information" in payload:
            raise RuntimeError(payload.get("Note") or payload.get("Information"))
        return payload

    def _require_key(self):
        if not self.enabled():
            raise RuntimeError("Alpha Vantage API key is not configured")


def _float(value):
    return round(float(value or 0), 4)


def _percent(value):
    return _float(str(value or "0").replace("%", ""))
