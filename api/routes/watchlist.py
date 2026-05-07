from flask import Blueprint, jsonify, request, session

from services.stock_service import stock_service
from services.watchlist_service import watchlist_service


watchlist_routes = Blueprint("watchlist_routes", __name__)


@watchlist_routes.route("", methods=["GET"])
def list_watchlist():
    username = session.get("username")
    if not username:
        return jsonify({"error": "Login required to access watchlist"}), 401
    symbols = watchlist_service.list_symbols(username=username)
    quotes = []
    errors = []
    for symbol in symbols:
        try:
            quotes.append(stock_service.get_quote(symbol)["data"])
        except Exception as exc:
            errors.append({"symbol": symbol, "error": str(exc)})
    return jsonify({"symbols": symbols, "quotes": quotes, "errors": errors})


@watchlist_routes.route("", methods=["POST"])
def add_watchlist():
    data = request.get_json(silent=True) or {}
    username = session.get("username")
    if not username:
        return jsonify({"error": "Login required to access watchlist"}), 401
    try:
        symbols = watchlist_service.add(data.get("symbol"), username=username)
        return jsonify({"symbols": symbols}), 201
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@watchlist_routes.route("/<symbol>", methods=["DELETE"])
def remove_watchlist(symbol):
    username = session.get("username")
    if not username:
        return jsonify({"error": "Login required to access watchlist"}), 401
    return jsonify({"symbols": watchlist_service.remove(symbol, username=username)})
