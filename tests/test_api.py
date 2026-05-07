import sys
from pathlib import Path
import json
import uuid

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"
sys.path.insert(0, str(API_DIR))

from app import create_app
from config import PREFERENCES_FILE, USERS_FILE, WATCHLIST_FILE
from services.dashboard_service import dashboard_service


def test_health():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_legacy_analyze_requires_symbol():
    app = create_app()
    client = app.test_client()
    response = client.post("/analyze", json={})
    assert response.status_code == 400
    assert response.get_json()["error"] == "No symbol provided"


def test_preferences_round_trip():
    original = _read_json(PREFERENCES_FILE)
    app = create_app()
    client = app.test_client()
    try:
        response = client.put("/api/user/preferences", json={"theme": "light", "defaultRange": "3mo"})
        assert response.status_code == 200
        payload = response.get_json()
        assert payload["theme"] == "light"
        assert payload["defaultRange"] == "3mo"
    finally:
        _write_json(PREFERENCES_FILE, original)


def test_watchlist_add_remove():
    original_users = _read_json(USERS_FILE)
    app = create_app()
    client = app.test_client()
    try:
        username = f"user_{uuid.uuid4().hex[:8]}"
        register_response = client.post("/api/user/register", json={"username": username, "password": "secret12", "displayName": "Test User"})
        assert register_response.status_code == 201

        add_response = client.post("/api/watchlist", json={"symbol": "IBM"})
        assert add_response.status_code == 201
        assert "IBM" in add_response.get_json()["symbols"]

        remove_response = client.delete("/api/watchlist/IBM")
        assert remove_response.status_code == 200
        assert "IBM" not in remove_response.get_json()["symbols"]
    finally:
        _write_json(USERS_FILE, original_users)


def test_watchlist_requires_login():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/watchlist")
    assert response.status_code == 401
    assert response.get_json()["error"] == "Login required to access watchlist"


def test_register_login_logout_flow():
    original_users = _read_json(USERS_FILE)
    app = create_app()
    client = app.test_client()
    username = f"user_{uuid.uuid4().hex[:8]}"
    try:
        register_response = client.post("/api/user/register", json={
            "username": username,
            "password": "secret12",
            "displayName": "A Test User",
        })
        assert register_response.status_code == 201
        payload = register_response.get_json()
        assert payload["user"]["username"] == username

        me_response = client.get("/api/user/me")
        assert me_response.status_code == 200
        assert me_response.get_json()["authenticated"] is True

        logout_response = client.post("/api/user/logout")
        assert logout_response.status_code == 200

        after_logout = client.get("/api/user/me")
        assert after_logout.get_json()["authenticated"] is False

        login_response = client.post("/api/user/login", json={"username": username, "password": "secret12"})
        assert login_response.status_code == 200
        assert login_response.get_json()["user"]["displayName"] == "A Test User"
    finally:
        _write_json(USERS_FILE, original_users)


def test_market_catalog_route():
    app = create_app()
    client = app.test_client()
    response = client.get("/api/stocks/catalog")
    assert response.status_code == 200
    payload = response.get_json()
    ids = {category["id"] for category in payload["categories"]}
    assert {"sp500", "nifty50", "sensex"} <= ids


def test_dashboard_route(monkeypatch):
    stub = {
        "regions": {
            "india": {"label": "India", "pulse": [], "core": [], "growth": [], "defensive": [], "technicals": {}, "chart": {"symbol": "^NSEI", "label": "NIFTY 50", "data": []}},
            "us": {"label": "United States", "pulse": [], "core": [], "growth": [], "defensive": [], "technicals": {}, "chart": {"symbol": "^GSPC", "label": "S&P 500", "data": []}},
        },
        "news": [],
    }
    monkeypatch.setattr(dashboard_service, "get_dashboard", lambda: stub)
    app = create_app()
    client = app.test_client()
    response = client.get("/api/stocks/dashboard")
    assert response.status_code == 200
    payload = response.get_json()
    assert set(payload["regions"].keys()) == {"india", "us"}


def _read_json(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path, payload):
    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
