from concurrent.futures import ThreadPoolExecutor, as_completed

from services.cache_service import cache
from services.news_service import news_service
from services.stock_service import stock_service


REGIONS = {
    "india": {
        "label": "India",
        "chart": {"symbol": "^NSEI", "label": "NIFTY 50"},
        "pulse": [
            {"symbol": "^NSEI", "label": "NIFTY 50", "kind": "index"},
            {"symbol": "^BSESN", "label": "SENSEX", "kind": "index"},
            {"symbol": "^NSEBANK", "label": "BANKNIFTY", "kind": "index"},
            {"symbol": "^CNXIT", "label": "NIFTY IT", "kind": "index"},
        ],
        "core": [
            {"symbol": "RELIANCE.NS", "label": "Reliance Industries"},
            {"symbol": "HDFCBANK.NS", "label": "HDFC Bank"},
            {"symbol": "TCS.NS", "label": "TCS"},
            {"symbol": "BHARTIARTL.NS", "label": "Bharti Airtel"},
            {"symbol": "LT.NS", "label": "Larsen & Toubro"},
        ],
        "growth": [
            {"symbol": "BEL.NS", "label": "Bharat Electronics"},
            {"symbol": "MARUTI.NS", "label": "Maruti Suzuki"},
            {"symbol": "TATAPOWER.NS", "label": "Tata Power"},
            {"symbol": "JKCEMENT.NS", "label": "JK Cement"},
            {"symbol": "COALINDIA.NS", "label": "Coal India"},
        ],
        "defensive": [
            {"symbol": "ITC.NS", "label": "ITC"},
            {"symbol": "HINDUNILVR.NS", "label": "Hindustan Unilever"},
        ],
    },
    "us": {
        "label": "United States",
        "chart": {"symbol": "^GSPC", "label": "S&P 500"},
        "pulse": [
            {"symbol": "^GSPC", "label": "S&P 500", "kind": "index"},
            {"symbol": "^DJI", "label": "Dow Jones", "kind": "index"},
            {"symbol": "^IXIC", "label": "NASDAQ Composite", "kind": "index"},
            {"symbol": "^RUT", "label": "Russell 2000", "kind": "index"},
        ],
        "core": [
            {"symbol": "MSFT", "label": "Microsoft"},
            {"symbol": "AAPL", "label": "Apple"},
            {"symbol": "AMZN", "label": "Amazon"},
            {"symbol": "JPM", "label": "JPMorgan Chase"},
            {"symbol": "XOM", "label": "Exxon Mobil"},
        ],
        "growth": [
            {"symbol": "NVDA", "label": "NVIDIA"},
            {"symbol": "META", "label": "Meta Platforms"},
            {"symbol": "AVGO", "label": "Broadcom"},
            {"symbol": "TSLA", "label": "Tesla"},
            {"symbol": "PLTR", "label": "Palantir"},
        ],
        "defensive": [
            {"symbol": "KO", "label": "Coca-Cola"},
            {"symbol": "PG", "label": "Procter & Gamble"},
        ],
    },
}


class DashboardService:
    def get_dashboard(self):
        cached = cache.get(("dashboard",))
        if cached is not None:
            return cached

        regions = {}
        with ThreadPoolExecutor(max_workers=len(REGIONS) + 1) as executor:
            region_futures = {
                executor.submit(self._build_region, region_id, config): region_id
                for region_id, config in REGIONS.items()
            }
            news_future = executor.submit(news_service.get_news, None, "general")

            for future in as_completed(region_futures):
                region_id = region_futures[future]
                regions[region_id] = future.result()

            news_payload = news_future.result()

        payload = {
            "regions": regions,
            "news": (news_payload.get("data") or [])[:4],
        }
        cache.set(("dashboard",), payload, 300)
        return payload

    def _build_region(self, region_id, config):
        pulse = self._hydrate_quotes(config["pulse"])
        core = self._hydrate_quotes(config["core"])
        growth = self._hydrate_quotes(config["growth"])
        defensive = self._hydrate_quotes(config["defensive"])
        technical_pool = core + growth + defensive
        chart_payload = stock_service.get_history(config["chart"]["symbol"], "1mo")

        return {
            "id": region_id,
            "label": config["label"],
            "pulse": pulse,
            "core": core,
            "growth": growth,
            "defensive": defensive,
            "technicals": self._technical_snapshot(technical_pool),
            "chart": {
                "symbol": config["chart"]["symbol"],
                "label": config["chart"]["label"],
                "data": chart_payload.get("data") or [],
                "provider": chart_payload.get("provider"),
            },
        }

    def _hydrate_quotes(self, items):
        symbols = [item["symbol"] for item in items]
        quotes_payload = stock_service.compare(symbols)
        quote_map = {item["symbol"]: item for item in quotes_payload.get("data") or []}
        merged = []
        for item in items:
            quote = quote_map.get(item["symbol"])
            if not quote:
                continue
            merged.append({**quote, **item})
        return merged

    def _technical_snapshot(self, quotes):
        symbols = [item["symbol"] for item in quotes]
        histories = self._fetch_histories(symbols, "1y")

        rows = []
        for quote in quotes:
            history = histories.get(quote["symbol"]) or []
            if len(history) < 20:
                continue
            closes = [point["close"] for point in history if point.get("close") is not None]
            if len(closes) < 20:
                continue

            latest = closes[-1]
            sma_200 = _sma(closes, 200)
            sma_50 = _sma(closes, 50)
            rsi_14 = _rsi(closes, 14)
            high_52 = max(closes)
            low_52 = min(closes)

            rows.append({
                "symbol": quote["symbol"],
                "label": quote.get("label") or quote.get("name") or quote["symbol"],
                "price": latest,
                "changePercent": quote.get("changePercent", 0),
                "sma50": sma_50,
                "sma200": sma_200,
                "rsi14": rsi_14,
                "aboveSma200": sma_200 is not None and latest > sma_200,
                "distanceTo52WeekHigh": _percentage_gap(latest, high_52),
                "distanceTo52WeekLow": _percentage_gap(latest, low_52),
                "momentum": _momentum_label(latest, sma_50, sma_200, rsi_14),
            })

        sorted_rows = sorted(rows, key=lambda item: item.get("changePercent", 0), reverse=True)
        return {
            "topGainers": sorted_rows[:3],
            "topLosers": list(reversed(sorted_rows[-3:])),
            "above200Sma": [item for item in rows if item["aboveSma200"]][:5],
            "rsiWatch": sorted(rows, key=lambda item: abs((item.get("rsi14") or 50) - 50), reverse=True)[:5],
        }

    def _fetch_histories(self, symbols, range_key):
        payloads = {}
        with ThreadPoolExecutor(max_workers=min(8, len(symbols) or 1)) as executor:
            futures = {executor.submit(stock_service.get_history, symbol, range_key): symbol for symbol in symbols}
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    payload = future.result()
                    payloads[symbol] = payload.get("data") or []
                except Exception:
                    payloads[symbol] = []
        return payloads


def _sma(values, window):
    if len(values) < window:
        return None
    segment = values[-window:]
    return round(sum(segment) / len(segment), 2)


def _rsi(values, period):
    if len(values) <= period:
        return None

    gains = []
    losses = []
    for idx in range(1, len(values)):
        delta = values[idx] - values[idx - 1]
        gains.append(max(delta, 0))
        losses.append(abs(min(delta, 0)))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for idx in range(period, len(gains)):
        avg_gain = ((avg_gain * (period - 1)) + gains[idx]) / period
        avg_loss = ((avg_loss * (period - 1)) + losses[idx]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def _percentage_gap(price, anchor):
    if not anchor:
        return None
    return round(((price - anchor) / anchor) * 100, 2)


def _momentum_label(price, sma_50, sma_200, rsi_14):
    if sma_50 and sma_200 and price > sma_50 > sma_200 and (rsi_14 or 0) >= 55:
        return "strong"
    if sma_200 and price < sma_200 and (rsi_14 or 100) <= 45:
        return "weak"
    return "mixed"


dashboard_service = DashboardService()
