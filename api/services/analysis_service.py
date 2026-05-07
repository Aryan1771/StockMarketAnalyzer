from run_cpp import run_cpp_analysis
from services.stock_service import stock_service
from utils import normalize_symbol


class AnalysisService:
    def analyze(self, symbol, range_key="10d"):
        symbol = normalize_symbol(symbol)
        history = stock_service.get_history(symbol, range_key=range_key)
        rows = history.get("data") or []
        if not rows:
            raise ValueError("Invalid symbol or no data")

        cpp_result = run_cpp_analysis(rows)
        return {
            "symbol": symbol,
            "history": rows,
            "analysis": cpp_result,
            "trend": self._trend(rows, cpp_result.get("metrics")),
            "provider": history.get("provider"),
            "fallbackErrors": history.get("errors", []),
        }

    def _trend(self, rows, metrics):
        if len(rows) < 2:
            return {"label": "neutral", "reason": "Not enough history"}

        first = rows[0]["close"]
        last = rows[-1]["close"]
        change_percent = ((last - first) / first * 100) if first else 0
        latest_ma = (metrics or {}).get("moving_average")

        if latest_ma and last > latest_ma and change_percent > 0:
            label = "bullish"
        elif latest_ma and last < latest_ma and change_percent < 0:
            label = "bearish"
        else:
            label = "neutral"

        return {
            "label": label,
            "changePercent": round(change_percent, 2),
            "reason": "Compares latest close, period change, and moving average.",
        }


analysis_service = AnalysisService()
