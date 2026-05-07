import time

import requests

from config import FINNHUB_API_KEY


class FinnhubProvider:
    name = "finnhub"
    base_url = "https://finnhub.io/api/v1"

    def __init__(self, api_key=None):
        self.api_key = api_key if api_key is not None else FINNHUB_API_KEY

    def enabled(self):
        return bool(self.api_key)

    def quote(self, symbol):
        self._require_key()
        quote = self._request("/quote", {"symbol": symbol})
        if quote.get("c") in (None, 0):
            raise ValueError("Finnhub returned no quote data")
        profile = {}
        try:
            profile = self._request("/stock/profile2", {"symbol": symbol})
        except Exception:
            profile = {}

        return {
            "symbol": symbol.upper(),
            "name": profile.get("name") or symbol.upper(),
            "price": round(float(quote.get("c") or 0), 4),
            "currency": profile.get("currency") or "USD",
            "change": round(float(quote.get("d") or 0), 4),
            "changePercent": round(float(quote.get("dp") or 0), 4),
            "volume": None,
            "marketCap": profile.get("marketCapitalization"),
            "provider": self.name,
        }

    def history(self, symbol, range_key="1mo"):
        self._require_key()
        days = {"10d": 10, "1mo": 31, "3mo": 93, "6mo": 186, "1y": 366}.get(range_key, 31)
        end = int(time.time())
        start = end - days * 24 * 60 * 60
        payload = self._request("/stock/candle", {
            "symbol": symbol,
            "resolution": "D",
            "from": start,
            "to": end,
        })
        if payload.get("s") != "ok":
            raise ValueError("Finnhub returned no historical data")

        rows = []
        for i, timestamp in enumerate(payload.get("t", [])):
            rows.append({
                "date": time.strftime("%Y-%m-%d", time.gmtime(timestamp)),
                "open": round(float(payload["o"][i]), 4),
                "high": round(float(payload["h"][i]), 4),
                "low": round(float(payload["l"][i]), 4),
                "close": round(float(payload["c"][i]), 4),
                "volume": int(payload["v"][i]),
            })
        return rows

    def search(self, query):
        self._require_key()
        payload = self._request("/search", {"q": query})
        return [{
            "symbol": item.get("symbol"),
            "name": item.get("description"),
            "exchange": "Finnhub",
            "provider": self.name,
        } for item in (payload.get("result") or [])[:8]]

    def news(self, symbol=None, category="general"):
        self._require_key()
        if symbol:
            payload = self._request("/company-news", {
                "symbol": symbol,
                "from": time.strftime("%Y-%m-%d", time.gmtime(time.time() - 7 * 86400)),
                "to": time.strftime("%Y-%m-%d", time.gmtime()),
            })
        else:
            payload = self._request("/news", {"category": category or "general"})
        return payload[:20] if isinstance(payload, list) else []

    def _request(self, path, params):
        response = requests.get(
            f"{self.base_url}{path}",
            params={**params, "token": self.api_key},
            timeout=12,
        )
        response.raise_for_status()
        return response.json()

    def _require_key(self):
        if not self.enabled():
            raise RuntimeError("Finnhub API key is not configured")
