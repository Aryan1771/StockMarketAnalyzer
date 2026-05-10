import logging
import os
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS

from config import FRONTEND_ORIGINS, SECRET_KEY, SESSION_COOKIE_SAMESITE, SESSION_COOKIE_SECURE
from routes.legacy import legacy_routes
from routes.news import news_routes
from routes.stocks import stocks_routes
from routes.user import user_routes
from routes.watchlist import watchlist_routes


def create_app():
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=SECRET_KEY,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=SESSION_COOKIE_SECURE,
        SESSION_COOKIE_SAMESITE=SESSION_COOKIE_SAMESITE,
    )
    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {"origins": FRONTEND_ORIGINS},
            r"/analyze": {"origins": FRONTEND_ORIGINS},
        },
    )

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )

    app.register_blueprint(legacy_routes)
    app.register_blueprint(stocks_routes, url_prefix="/api/stocks")
    app.register_blueprint(news_routes, url_prefix="/api/news")
    app.register_blueprint(watchlist_routes, url_prefix="/api/watchlist")
    app.register_blueprint(user_routes, url_prefix="/api/user")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    @app.route("/ping")
    def ping():
        return jsonify({
            "ok": True,
            "service": "stockmarketanalyzer-backend",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        })

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(error):
        app.logger.exception("Unhandled server error: %s", error)
        return jsonify({"error": "Unexpected server error"}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
