import logging

import yfinance as yf


LOGGER = logging.getLogger(__name__)


class YahooProvider:
    name = "yahoo"

    def quote(self, symbol):
        ticker = yf.Ticker(symbol)
        fast_info = getattr(ticker, "fast_info", {}) or {}
        hist = ticker.history(period="5d")
        if hist.empty:
            raise ValueError("Yahoo Finance returned no quote data")

        last = hist.iloc[-1]
        prev_close = _safe_float(fast_info.get("previous_close"))
        if prev_close is None and len(hist) > 1:
            prev_close = _safe_float(hist.iloc[-2]["Close"])

        price = _safe_float(fast_info.get("last_price")) or _safe_float(last["Close"])
        change = price - prev_close if prev_close else 0
        change_percent = (change / prev_close * 100) if prev_close else 0

        info = {}
        try:
            info = ticker.get_info() or {}
        except Exception as exc:
            LOGGER.debug("Yahoo info unavailable for %s: %s", symbol, exc)

        return {
            "symbol": symbol.upper(),
            "name": info.get("shortName") or info.get("longName") or symbol.upper(),
            "price": round(price, 4),
            "currency": fast_info.get("currency") or info.get("currency") or "USD",
            "change": round(change, 4),
            "changePercent": round(change_percent, 4),
            "volume": int(last.get("Volume", 0) or 0),
            "marketCap": _safe_int(fast_info.get("market_cap") or info.get("marketCap")),
            "provider": self.name,
        }

    def history(self, symbol, range_key="1mo"):
        period = {
            "10d": "10d",
            "1mo": "1mo",
            "3mo": "3mo",
            "6mo": "6mo",
            "1y": "1y",
            "5y": "5y",
        }.get(range_key, "1mo")
        hist = yf.Ticker(symbol).history(period=period)
        if hist.empty:
            raise ValueError("Yahoo Finance returned no historical data")

        rows = []
        for index, row in hist.iterrows():
            rows.append({
                "date": str(index.date()),
                "open": _safe_float(row["Open"]),
                "high": _safe_float(row["High"]),
                "low": _safe_float(row["Low"]),
                "close": _safe_float(row["Close"]),
                "volume": int(row["Volume"] or 0),
            })

        return rows

    def search(self, query):
        if not query:
            return []

        candidates = [query.upper()]
        common = {
            "APPLE": "AAPL",
            "MICROSOFT": "MSFT",
            "GOOGLE": "GOOGL",
            "ALPHABET": "GOOGL",
            "AMAZON": "AMZN",
            "TESLA": "TSLA",
            "NVIDIA": "NVDA",
            "META": "META",
        }
        if query.upper() in common:
            candidates.insert(0, common[query.upper()])

        results = []
        for symbol in dict.fromkeys(candidates):
            try:
                quote = self.quote(symbol)
                results.append({
                    "symbol": quote["symbol"],
                    "name": quote["name"],
                    "exchange": "Yahoo Finance",
                    "provider": self.name,
                })
            except Exception as exc:
                LOGGER.debug("Yahoo search candidate failed for %s: %s", symbol, exc)

        return results


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_int(value):
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None
