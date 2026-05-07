import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"
sys.path.insert(0, str(API_DIR))

from services.stock_service import StockService


class ProviderStub:
    name = "stub"

    def quote(self, symbol):
        return {"symbol": symbol, "price": 10}

    def history(self, symbol, range_key="1mo"):
        return [{"date": "2026-01-01", "close": 10}]

    def search(self, query):
        return [{"symbol": query.upper(), "name": "Stub Inc", "exchange": "Test", "provider": "stub"}]


def test_provider_normalization_shape():
    service = StockService()
    service.providers = [ProviderStub()]
    quote = service.get_quote("abc")
    assert quote["data"]["symbol"] == "ABC"
    assert quote["provider"] == "stub"


def test_search_deduplicates_symbols():
    service = StockService()
    service.providers = [ProviderStub(), ProviderStub()]
    service._catalog_search = lambda query: []
    results = service.search("abc")
    assert len(results["data"]) == 1


def test_search_includes_catalog_symbols_for_india_names():
    service = StockService()
    service.providers = []
    results = service.search("ong")
    symbols = [item["symbol"] for item in results["data"]]
    assert "ONGC.NS" in symbols
