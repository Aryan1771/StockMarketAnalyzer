from flask import Blueprint, jsonify, request

from services.news_service import news_service


news_routes = Blueprint("news_routes", __name__)


@news_routes.route("")
def news():
    symbol = request.args.get("symbol")
    category = request.args.get("category", "general")
    return jsonify(news_service.get_news(symbol=symbol, category=category))
