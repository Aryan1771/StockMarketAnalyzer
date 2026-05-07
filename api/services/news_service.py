import time

from services.cache_service import cache
from services.stock_providers.alpha_vantage_provider import AlphaVantageProvider
from services.stock_providers.finnhub_provider import FinnhubProvider
from utils import sentiment_for_text

DEFAULT_MARKET_SYMBOLS = ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL"]


class NewsService:
    def __init__(self):
        self.finnhub = FinnhubProvider()
        self.alpha_vantage = AlphaVantageProvider()

    def get_news(self, symbol=None, category="general"):
        key = ("news", (symbol or "").upper(), category or "general")
        cached = cache.get(key)
        if cached:
            return {**cached, "cached": True}

        errors = []
        merged = []
        providers_used = []

        providers = [
            ("finnhub", lambda: self.finnhub.news(symbol=symbol, category=category)),
            ("alpha_vantage", lambda: self.alpha_vantage.news(symbol=symbol, category=category)),
        ]

        for provider_name, fetch in providers:
            try:
                articles = fetch()
                if articles:
                    providers_used.append(provider_name)
                    merged.extend(self._normalize(item, provider_name) for item in articles)
            except Exception as exc:
                errors.append({"provider": provider_name, "error": str(exc)})

        if not merged and not symbol and (category or "general") == "general":
            merged.extend(self._market_basket_news(providers_used, errors))

        deduped = self._dedupe_and_sort(merged)
        if not deduped:
            deduped = [self._normalize(item, "fallback") for item in self._fallback_news(symbol, errors)]

        provider_label = "multiple" if len(providers_used) > 1 else (providers_used[0] if providers_used else "fallback")
        payload = {"data": deduped[:20], "provider": provider_label, "errors": errors}
        cache.set(key, payload, 300)
        return {**payload, "cached": False}

    def _market_basket_news(self, providers_used, errors):
        merged = []
        symbol_errors = {}

        providers = [
            ("finnhub", self.finnhub),
            ("alpha_vantage", self.alpha_vantage),
        ]
        for provider_name, provider in providers:
            if not provider.enabled():
                continue

            provider_articles = []
            for market_symbol in DEFAULT_MARKET_SYMBOLS:
                try:
                    provider_articles.extend(provider.news(symbol=market_symbol, category="general") or [])
                    if len(provider_articles) >= 12:
                        break
                except Exception as exc:
                    symbol_errors[provider_name] = str(exc)
                    break

            if provider_articles:
                providers_used.append(provider_name)
                merged.extend(self._normalize(item, provider_name) for item in provider_articles)
            elif provider_name in symbol_errors:
                errors.append({"provider": provider_name, "error": symbol_errors[provider_name]})

        return merged

    def _normalize(self, item, provider):
        title = item.get("headline") or item.get("title") or "Market update"
        summary = item.get("summary") or item.get("description") or ""
        source = item.get("source") or "Market desk"
        if isinstance(source, dict):
            source = source.get("name") or "Market desk"

        published = item.get("datetime") or item.get("publishedAt") or item.get("time_published") or int(time.time())
        return {
            "id": str(item.get("id") or item.get("url") or title),
            "title": title,
            "summary": summary,
            "source": source,
            "provider": provider,
            "url": item.get("url") or "#",
            "image": item.get("image") or item.get("banner_image") or item.get("urlToImage") or "",
            "publishedAt": self._normalize_published_at(published),
            "sentiment": item.get("overall_sentiment_label", "").lower().replace("_", " ") or sentiment_for_text(f"{title} {summary}"),
        }

    def _normalize_published_at(self, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            try:
                if len(value) == 15 and "T" in value:
                    parsed = time.strptime(value, "%Y%m%dT%H%M%S")
                    return int(time.mktime(parsed))
                if value.isdigit():
                    return int(value)
            except Exception:
                return int(time.time())
            try:
                parsed = time.strptime(value[:19], "%Y-%m-%dT%H:%M:%S")
                return int(time.mktime(parsed))
            except Exception:
                try:
                    parsed = time.strptime(value[:19], "%Y-%m-%d %H:%M:%S")
                    return int(time.mktime(parsed))
                except Exception:
                    return int(time.time())
        return int(time.time())

    def _dedupe_and_sort(self, items):
        seen = set()
        unique = []
        for item in items:
            key = (item.get("url") or "#", item.get("title") or "")
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        unique.sort(key=lambda article: article.get("publishedAt", 0), reverse=True)
        return unique

    def _fallback_news(self, symbol, errors):
        target = symbol.upper() if symbol else "the market"
        setup_needed = not self.finnhub.enabled() and not self.alpha_vantage.enabled()
        if setup_needed:
            summary = "Configure a Finnhub or Alpha Vantage API key to unlock live market news. This placeholder keeps the news page usable during setup."
        elif errors:
            summary = "Live news providers are configured, but the current request returned no stories or hit a provider limit. Try a symbol search like AAPL or check API rate limits."
        else:
            summary = "Live news providers did not return stories for this request yet. Try a symbol search like AAPL, MSFT, or ONGC.NS."
        return [
            {
                "headline": f"Latest {target} watchlist briefing",
                "summary": summary,
                "source": "StockMarketAnalyzer",
                "url": "#",
            }
        ]


news_service = NewsService()
