import csv
import io
import logging

import requests

from services.cache_service import cache


LOGGER = logging.getLogger(__name__)

SP500_CSV_URL = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"


class MarketCatalogService:
    def get_catalog(self):
        cached = cache.get(("market-catalog",))
        if cached is not None:
            return {**cached, "cached": True}

        categories = [
            {
                "id": "sp500",
                "label": "S&P 500",
                "market": "US",
                "description": "Large-cap United States equities.",
                "source": "Remote constituent CSV with local fallback",
                "stocks": self._load_sp500(),
            },
            {
                "id": "nifty50",
                "label": "Nifty 50",
                "market": "India",
                "description": "Large-cap NSE constituents.",
                "source": "Built-in curated constituent list",
                "stocks": NIFTY50_STOCKS,
            },
            {
                "id": "sensex",
                "label": "Sensex",
                "market": "India",
                "description": "Flagship BSE large-cap constituents.",
                "source": "Built-in curated constituent list",
                "stocks": SENSEX_STOCKS,
            },
        ]

        payload = {
            "categories": [
                {**category, "count": len(category["stocks"])}
                for category in categories
            ],
            "providers": ["yahoo", "alpha_vantage", "finnhub"],
        }
        cache.set(("market-catalog",), payload, 3600)
        return {**payload, "cached": False}

    def _load_sp500(self):
        cached = cache.get(("market-catalog-sp500",))
        if cached is not None:
            return cached

        try:
            response = requests.get(SP500_CSV_URL, timeout=12)
            response.raise_for_status()
            reader = csv.DictReader(io.StringIO(response.text))
            stocks = []
            for row in reader:
                symbol = (row.get("Symbol") or "").strip().replace(".", "-").upper()
                if not symbol:
                    continue
                stocks.append({
                    "symbol": symbol,
                    "displaySymbol": symbol,
                    "name": (row.get("Security") or symbol).strip(),
                    "sector": (row.get("GICS Sector") or "Diversified").strip(),
                    "exchange": "US",
                })
            if stocks:
                cache.set(("market-catalog-sp500",), stocks, 24 * 3600)
                return stocks
        except Exception as exc:
            LOGGER.warning("Falling back to built-in S&P 500 subset: %s", exc)

        cache.set(("market-catalog-sp500",), SP500_FALLBACK_STOCKS, 24 * 3600)
        return SP500_FALLBACK_STOCKS


market_catalog_service = MarketCatalogService()


SP500_FALLBACK_STOCKS = [
    {"symbol": "AAPL", "displaySymbol": "AAPL", "name": "Apple Inc.", "sector": "Information Technology", "exchange": "US"},
    {"symbol": "MSFT", "displaySymbol": "MSFT", "name": "Microsoft Corporation", "sector": "Information Technology", "exchange": "US"},
    {"symbol": "AMZN", "displaySymbol": "AMZN", "name": "Amazon.com, Inc.", "sector": "Consumer Discretionary", "exchange": "US"},
    {"symbol": "NVDA", "displaySymbol": "NVDA", "name": "NVIDIA Corporation", "sector": "Information Technology", "exchange": "US"},
    {"symbol": "GOOGL", "displaySymbol": "GOOGL", "name": "Alphabet Inc. Class A", "sector": "Communication Services", "exchange": "US"},
    {"symbol": "META", "displaySymbol": "META", "name": "Meta Platforms, Inc.", "sector": "Communication Services", "exchange": "US"},
    {"symbol": "BRK-B", "displaySymbol": "BRK-B", "name": "Berkshire Hathaway Inc. Class B", "sector": "Financials", "exchange": "US"},
    {"symbol": "LLY", "displaySymbol": "LLY", "name": "Eli Lilly and Company", "sector": "Health Care", "exchange": "US"},
    {"symbol": "JPM", "displaySymbol": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials", "exchange": "US"},
    {"symbol": "XOM", "displaySymbol": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "exchange": "US"},
]


NIFTY50_STOCKS = [
    {"symbol": "ADANIENT.NS", "displaySymbol": "ADANIENT", "name": "Adani Enterprises", "sector": "Industrials", "exchange": "NSE"},
    {"symbol": "ADANIPORTS.NS", "displaySymbol": "ADANIPORTS", "name": "Adani Ports and SEZ", "sector": "Industrials", "exchange": "NSE"},
    {"symbol": "APOLLOHOSP.NS", "displaySymbol": "APOLLOHOSP", "name": "Apollo Hospitals", "sector": "Health Care", "exchange": "NSE"},
    {"symbol": "ASIANPAINT.NS", "displaySymbol": "ASIANPAINT", "name": "Asian Paints", "sector": "Materials", "exchange": "NSE"},
    {"symbol": "AXISBANK.NS", "displaySymbol": "AXISBANK", "name": "Axis Bank", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "BAJAJ-AUTO.NS", "displaySymbol": "BAJAJ-AUTO", "name": "Bajaj Auto", "sector": "Consumer Discretionary", "exchange": "NSE"},
    {"symbol": "BAJFINANCE.NS", "displaySymbol": "BAJFINANCE", "name": "Bajaj Finance", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "BAJAJFINSV.NS", "displaySymbol": "BAJAJFINSV", "name": "Bajaj Finserv", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "BEL.NS", "displaySymbol": "BEL", "name": "Bharat Electronics", "sector": "Industrials", "exchange": "NSE"},
    {"symbol": "BHARTIARTL.NS", "displaySymbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Communication Services", "exchange": "NSE"},
    {"symbol": "BPCL.NS", "displaySymbol": "BPCL", "name": "Bharat Petroleum", "sector": "Energy", "exchange": "NSE"},
    {"symbol": "BRITANNIA.NS", "displaySymbol": "BRITANNIA", "name": "Britannia Industries", "sector": "Consumer Staples", "exchange": "NSE"},
    {"symbol": "CIPLA.NS", "displaySymbol": "CIPLA", "name": "Cipla", "sector": "Health Care", "exchange": "NSE"},
    {"symbol": "COALINDIA.NS", "displaySymbol": "COALINDIA", "name": "Coal India", "sector": "Energy", "exchange": "NSE"},
    {"symbol": "DRREDDY.NS", "displaySymbol": "DRREDDY", "name": "Dr. Reddy's Laboratories", "sector": "Health Care", "exchange": "NSE"},
    {"symbol": "EICHERMOT.NS", "displaySymbol": "EICHERMOT", "name": "Eicher Motors", "sector": "Consumer Discretionary", "exchange": "NSE"},
    {"symbol": "ETERNAL.NS", "displaySymbol": "ETERNAL", "name": "Eternal", "sector": "Consumer Discretionary", "exchange": "NSE"},
    {"symbol": "GRASIM.NS", "displaySymbol": "GRASIM", "name": "Grasim Industries", "sector": "Materials", "exchange": "NSE"},
    {"symbol": "HCLTECH.NS", "displaySymbol": "HCLTECH", "name": "HCL Technologies", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "HDFCBANK.NS", "displaySymbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "HDFCLIFE.NS", "displaySymbol": "HDFCLIFE", "name": "HDFC Life Insurance", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "HEROMOTOCO.NS", "displaySymbol": "HEROMOTOCO", "name": "Hero MotoCorp", "sector": "Consumer Discretionary", "exchange": "NSE"},
    {"symbol": "HINDALCO.NS", "displaySymbol": "HINDALCO", "name": "Hindalco Industries", "sector": "Materials", "exchange": "NSE"},
    {"symbol": "HINDUNILVR.NS", "displaySymbol": "HINDUNILVR", "name": "Hindustan Unilever", "sector": "Consumer Staples", "exchange": "NSE"},
    {"symbol": "ICICIBANK.NS", "displaySymbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "INDUSINDBK.NS", "displaySymbol": "INDUSINDBK", "name": "IndusInd Bank", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "INFY.NS", "displaySymbol": "INFY", "name": "Infosys", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "ITC.NS", "displaySymbol": "ITC", "name": "ITC", "sector": "Consumer Staples", "exchange": "NSE"},
    {"symbol": "JIOFIN.NS", "displaySymbol": "JIOFIN", "name": "Jio Financial Services", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "JSWSTEEL.NS", "displaySymbol": "JSWSTEEL", "name": "JSW Steel", "sector": "Materials", "exchange": "NSE"},
    {"symbol": "KOTAKBANK.NS", "displaySymbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "LT.NS", "displaySymbol": "LT", "name": "Larsen & Toubro", "sector": "Industrials", "exchange": "NSE"},
    {"symbol": "M&M.NS", "displaySymbol": "M&M", "name": "Mahindra & Mahindra", "sector": "Consumer Discretionary", "exchange": "NSE"},
    {"symbol": "MARUTI.NS", "displaySymbol": "MARUTI", "name": "Maruti Suzuki", "sector": "Consumer Discretionary", "exchange": "NSE"},
    {"symbol": "NESTLEIND.NS", "displaySymbol": "NESTLEIND", "name": "Nestle India", "sector": "Consumer Staples", "exchange": "NSE"},
    {"symbol": "NTPC.NS", "displaySymbol": "NTPC", "name": "NTPC", "sector": "Utilities", "exchange": "NSE"},
    {"symbol": "ONGC.NS", "displaySymbol": "ONGC", "name": "Oil & Natural Gas Corporation", "sector": "Energy", "exchange": "NSE"},
    {"symbol": "POWERGRID.NS", "displaySymbol": "POWERGRID", "name": "Power Grid Corporation", "sector": "Utilities", "exchange": "NSE"},
    {"symbol": "RELIANCE.NS", "displaySymbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy", "exchange": "NSE"},
    {"symbol": "SBILIFE.NS", "displaySymbol": "SBILIFE", "name": "SBI Life Insurance", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "SBIN.NS", "displaySymbol": "SBIN", "name": "State Bank of India", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "SHRIRAMFIN.NS", "displaySymbol": "SHRIRAMFIN", "name": "Shriram Finance", "sector": "Financials", "exchange": "NSE"},
    {"symbol": "SUNPHARMA.NS", "displaySymbol": "SUNPHARMA", "name": "Sun Pharmaceutical", "sector": "Health Care", "exchange": "NSE"},
    {"symbol": "TATACONSUM.NS", "displaySymbol": "TATACONSUM", "name": "Tata Consumer Products", "sector": "Consumer Staples", "exchange": "NSE"},
    {"symbol": "TATAMOTORS.NS", "displaySymbol": "TATAMOTORS", "name": "Tata Motors", "sector": "Consumer Discretionary", "exchange": "NSE"},
    {"symbol": "TATASTEEL.NS", "displaySymbol": "TATASTEEL", "name": "Tata Steel", "sector": "Materials", "exchange": "NSE"},
    {"symbol": "TCS.NS", "displaySymbol": "TCS", "name": "Tata Consultancy Services", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "TECHM.NS", "displaySymbol": "TECHM", "name": "Tech Mahindra", "sector": "Information Technology", "exchange": "NSE"},
    {"symbol": "TITAN.NS", "displaySymbol": "TITAN", "name": "Titan Company", "sector": "Consumer Discretionary", "exchange": "NSE"},
    {"symbol": "TRENT.NS", "displaySymbol": "TRENT", "name": "Trent", "sector": "Consumer Discretionary", "exchange": "NSE"},
    {"symbol": "ULTRACEMCO.NS", "displaySymbol": "ULTRACEMCO", "name": "UltraTech Cement", "sector": "Materials", "exchange": "NSE"},
    {"symbol": "WIPRO.NS", "displaySymbol": "WIPRO", "name": "Wipro", "sector": "Information Technology", "exchange": "NSE"},
]


SENSEX_STOCKS = [
    {"symbol": "ADANIPORTS.NS", "displaySymbol": "ADANIPORTS", "name": "Adani Ports and SEZ", "sector": "Industrials", "exchange": "BSE Sensex"},
    {"symbol": "ASIANPAINT.NS", "displaySymbol": "ASIANPAINT", "name": "Asian Paints", "sector": "Materials", "exchange": "BSE Sensex"},
    {"symbol": "AXISBANK.NS", "displaySymbol": "AXISBANK", "name": "Axis Bank", "sector": "Financials", "exchange": "BSE Sensex"},
    {"symbol": "BAJFINANCE.NS", "displaySymbol": "BAJFINANCE", "name": "Bajaj Finance", "sector": "Financials", "exchange": "BSE Sensex"},
    {"symbol": "BAJAJFINSV.NS", "displaySymbol": "BAJAJFINSV", "name": "Bajaj Finserv", "sector": "Financials", "exchange": "BSE Sensex"},
    {"symbol": "BHARTIARTL.NS", "displaySymbol": "BHARTIARTL", "name": "Bharti Airtel", "sector": "Communication Services", "exchange": "BSE Sensex"},
    {"symbol": "HCLTECH.NS", "displaySymbol": "HCLTECH", "name": "HCL Technologies", "sector": "Information Technology", "exchange": "BSE Sensex"},
    {"symbol": "HDFCBANK.NS", "displaySymbol": "HDFCBANK", "name": "HDFC Bank", "sector": "Financials", "exchange": "BSE Sensex"},
    {"symbol": "HINDUNILVR.NS", "displaySymbol": "HINDUNILVR", "name": "Hindustan Unilever", "sector": "Consumer Staples", "exchange": "BSE Sensex"},
    {"symbol": "ICICIBANK.NS", "displaySymbol": "ICICIBANK", "name": "ICICI Bank", "sector": "Financials", "exchange": "BSE Sensex"},
    {"symbol": "INDUSINDBK.NS", "displaySymbol": "INDUSINDBK", "name": "IndusInd Bank", "sector": "Financials", "exchange": "BSE Sensex"},
    {"symbol": "INFY.NS", "displaySymbol": "INFY", "name": "Infosys", "sector": "Information Technology", "exchange": "BSE Sensex"},
    {"symbol": "ITC.NS", "displaySymbol": "ITC", "name": "ITC", "sector": "Consumer Staples", "exchange": "BSE Sensex"},
    {"symbol": "KOTAKBANK.NS", "displaySymbol": "KOTAKBANK", "name": "Kotak Mahindra Bank", "sector": "Financials", "exchange": "BSE Sensex"},
    {"symbol": "LT.NS", "displaySymbol": "LT", "name": "Larsen & Toubro", "sector": "Industrials", "exchange": "BSE Sensex"},
    {"symbol": "MARUTI.NS", "displaySymbol": "MARUTI", "name": "Maruti Suzuki", "sector": "Consumer Discretionary", "exchange": "BSE Sensex"},
    {"symbol": "M&M.NS", "displaySymbol": "M&M", "name": "Mahindra & Mahindra", "sector": "Consumer Discretionary", "exchange": "BSE Sensex"},
    {"symbol": "NESTLEIND.NS", "displaySymbol": "NESTLEIND", "name": "Nestle India", "sector": "Consumer Staples", "exchange": "BSE Sensex"},
    {"symbol": "NTPC.NS", "displaySymbol": "NTPC", "name": "NTPC", "sector": "Utilities", "exchange": "BSE Sensex"},
    {"symbol": "POWERGRID.NS", "displaySymbol": "POWERGRID", "name": "Power Grid Corporation", "sector": "Utilities", "exchange": "BSE Sensex"},
    {"symbol": "RELIANCE.NS", "displaySymbol": "RELIANCE", "name": "Reliance Industries", "sector": "Energy", "exchange": "BSE Sensex"},
    {"symbol": "SBIN.NS", "displaySymbol": "SBIN", "name": "State Bank of India", "sector": "Financials", "exchange": "BSE Sensex"},
    {"symbol": "SUNPHARMA.NS", "displaySymbol": "SUNPHARMA", "name": "Sun Pharmaceutical", "sector": "Health Care", "exchange": "BSE Sensex"},
    {"symbol": "TATACONSUM.NS", "displaySymbol": "TATACONSUM", "name": "Tata Consumer Products", "sector": "Consumer Staples", "exchange": "BSE Sensex"},
    {"symbol": "TATAMOTORS.NS", "displaySymbol": "TATAMOTORS", "name": "Tata Motors", "sector": "Consumer Discretionary", "exchange": "BSE Sensex"},
    {"symbol": "TATASTEEL.NS", "displaySymbol": "TATASTEEL", "name": "Tata Steel", "sector": "Materials", "exchange": "BSE Sensex"},
    {"symbol": "TCS.NS", "displaySymbol": "TCS", "name": "Tata Consultancy Services", "sector": "Information Technology", "exchange": "BSE Sensex"},
    {"symbol": "TECHM.NS", "displaySymbol": "TECHM", "name": "Tech Mahindra", "sector": "Information Technology", "exchange": "BSE Sensex"},
    {"symbol": "TITAN.NS", "displaySymbol": "TITAN", "name": "Titan Company", "sector": "Consumer Discretionary", "exchange": "BSE Sensex"},
    {"symbol": "ULTRACEMCO.NS", "displaySymbol": "ULTRACEMCO", "name": "UltraTech Cement", "sector": "Materials", "exchange": "BSE Sensex"},
]
