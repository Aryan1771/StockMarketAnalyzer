from flask import Blueprint, jsonify, request

from services.analysis_service import analysis_service
from services.dashboard_service import dashboard_service
from services.market_catalog_service import market_catalog_service
from services.stock_service import stock_service
from utils import normalize_symbol


stocks_routes = Blueprint("stocks_routes", __name__)


@stocks_routes.route("/search")
def search():
    query = request.args.get("q", "")
    return jsonify(stock_service.search(query))


@stocks_routes.route("/overview")
def overview():
    return jsonify(stock_service.market_overview())


@stocks_routes.route("/dashboard")
def dashboard():
    return jsonify(dashboard_service.get_dashboard())


@stocks_routes.route("/catalog")
def catalog():
    return jsonify(market_catalog_service.get_catalog())


@stocks_routes.route("/compare")
def compare():
    symbols = [normalize_symbol(item) for item in request.args.get("symbols", "").split(",") if item.strip()]
    if not symbols:
        return jsonify({"error": "At least one symbol is required"}), 400
    return jsonify(stock_service.compare(symbols))


@stocks_routes.route("/<symbol>/quote")
def quote(symbol):
    try:
        return jsonify(stock_service.get_quote(symbol))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


@stocks_routes.route("/<symbol>/history")
def history(symbol):
    range_key = request.args.get("range", "1mo")
    try:
        return jsonify(stock_service.get_history(symbol, range_key=range_key))
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502


@stocks_routes.route("/<symbol>/analysis")
def analysis(symbol):
    range_key = request.args.get("range", "10d")
    try:
        return jsonify(analysis_service.analyze(symbol, range_key=range_key))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502
