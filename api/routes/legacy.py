from flask import Blueprint, jsonify, request

from services.analysis_service import analysis_service


legacy_routes = Blueprint("legacy_routes", __name__)


@legacy_routes.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json(silent=True) or {}
    symbol = data.get("symbol")

    if not symbol:
        return jsonify({"error": "No symbol provided"}), 400

    try:
        result = analysis_service.analyze(symbol, range_key="10d")
        return jsonify({
            "symbol": result["symbol"],
            "analysis": result["analysis"],
            "trend": result["trend"],
            "provider": result["provider"],
            "fallbackErrors": result["fallbackErrors"],
        })
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        return jsonify({"error": str(exc)}), 502
