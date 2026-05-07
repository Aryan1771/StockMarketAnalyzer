import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import CACHE_TTL_SECONDS, DEFAULT_SYMBOLS
from services.cache_service import cache
from services.market_catalog_service import market_catalog_service
from services.stock_providers.alpha_vantage_provider import AlphaVantageProvider
from services.stock_providers.finnhub_provider import FinnhubProvider
from services.stock_providers.yahoo_provider import YahooProvider
from utils import normalize_symbol


LOGGER = logging.getLogger(__name__)


class StockService:
    def __init__(self):
        self.providers = [YahooProvider(), AlphaVantageProvider(), FinnhubProvider()]

    def get_quote(self, symbol):
        symbol = normalize_symbol(symbol)
        return self._with_cache(("quote", symbol), lambda: self._first_success("quote", symbol))

    def get_history(self, symbol, range_key="1mo"):
        symbol = normalize_symbol(symbol)
        return self._with_cache(
            ("history", symbol, range_key),
            lambda: self._first_success("history", symbol, range_key),
        )

    def search(self, query):
        query = (query or "").strip()
        if not query:
            return {"data": [], "provider": None, "errors": []}
        return self._with_cache(("search", query.upper()), lambda: self._search(query))

    def compare(self, symbols):
        quotes = []
        errors = []

        normalized_symbols = [normalize_symbol(symbol) for symbol in symbols if normalize_symbol(symbol)]
        if not normalized_symbols:
            return {"data": quotes, "errors": errors}

        with ThreadPoolExecutor(max_workers=min(8, len(normalized_symbols))) as executor:
            futures = {
                executor.submit(self.get_quote, symbol): symbol
                for symbol in normalized_symbols
            }
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    quotes.append(future.result()["data"])
                except Exception as exc:
                    errors.append({"symbol": symbol, "error": str(exc)})
        return {"data": quotes, "errors": errors}

    def market_overview(self):
        quotes = []
        for symbol in DEFAULT_SYMBOLS:
            try:
                quotes.append(self.get_quote(symbol)["data"])
            except Exception as exc:
                LOGGER.info("Overview quote failed for %s: %s", symbol, exc)
        return {"data": quotes}

    def _with_cache(self, key, producer):
        cached = cache.get(key)
        if cached is not None:
            return {**cached, "cached": True}

        value = producer()
        cache.set(key, value, CACHE_TTL_SECONDS)
        return {**value, "cached": False}

    def _first_success(self, method_name, *args):
        errors = []
        for provider in self.providers:
            try:
                method = getattr(provider, method_name)
                return {
                    "data": method(*args),
                    "provider": provider.name,
                    "errors": errors,
                }
            except Exception as exc:
                errors.append({"provider": provider.name, "error": str(exc)})
                LOGGER.info("%s provider failed for %s: %s", provider.name, method_name, exc)

        raise RuntimeError(f"No stock provider could satisfy {method_name}")

    def _search(self, query):
        errors = []
        seen = set()
        results = []

        for item in self._catalog_search(query):
            symbol = normalize_symbol(item.get("symbol"))
            if symbol and symbol not in seen:
                seen.add(symbol)
                results.append({**item, "symbol": symbol})

        for provider in self.providers:
            try:
                for item in provider.search(query):
                    symbol = normalize_symbol(item.get("symbol"))
                    if symbol and symbol not in seen:
                        seen.add(symbol)
                        results.append({**item, "symbol": symbol})
                if len(results) >= 10:
                    return {"data": results[:10], "provider": provider.name, "errors": errors}
            except Exception as exc:
                errors.append({"provider": provider.name, "error": str(exc)})
        provider_label = "catalog" if results else None
        return {"data": results[:10], "provider": provider_label, "errors": errors}

    def _catalog_search(self, query):
        query_lower = (query or "").strip().lower()
        if not query_lower:
            return []

        catalog = market_catalog_service.get_catalog()
        matches = []
        seen = set()

        for category in catalog.get("categories", []):
            for stock in category.get("stocks", []):
                display_symbol = (stock.get("displaySymbol") or "").strip()
                symbol = normalize_symbol(stock.get("symbol"))
                name = (stock.get("name") or "").strip()
                exchange = (stock.get("exchange") or "").strip()
                haystack = " ".join(filter(None, [display_symbol, symbol, name, exchange, category.get("label"), category.get("market")])).lower()

                if query_lower not in haystack:
                    continue
                if symbol in seen:
                    continue

                seen.add(symbol)
                matches.append({
                    "symbol": symbol,
                    "name": name or display_symbol or symbol,
                    "exchange": exchange or category.get("market") or "Catalog",
                    "provider": "catalog",
                    "displaySymbol": display_symbol or symbol,
                    "category": category.get("label"),
                    "_rank": self._catalog_rank(query_lower, display_symbol, symbol, name),
                })

        matches.sort(key=lambda item: (item["_rank"], item["displaySymbol"]))
        return [{key: value for key, value in item.items() if key != "_rank"} for item in matches[:10]]

    def _catalog_rank(self, query_lower, display_symbol, symbol, name):
        candidates = [
            (display_symbol or "").lower(),
            (symbol or "").lower(),
            (name or "").lower(),
        ]
        if any(candidate == query_lower for candidate in candidates):
            return 0
        if any(candidate.startswith(query_lower) for candidate in candidates):
            return 1
        if query_lower in (name or "").lower():
            return 2
        return 3


stock_service = StockService()
