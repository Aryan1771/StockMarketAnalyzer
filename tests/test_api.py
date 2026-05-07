import sys
from pathlib import Path
import json
import uuid
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[1]
API_DIR = ROOT / "api"
sys.path.insert(0, str(API_DIR))

from app import create_app
from config import PREFERENCES_FILE, USERS_FILE, WATCHLIST_FILE
from services.cache_service import cache
from services.dashboard_service import dashboard_service
from services.news_service import news_service
from services.user_service import db_service as user_db_service


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
        register_response = client.post("/api/user/register", json={"username": username, "password": "Secret12", "displayName": "Test User"})
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
            "password": "Secret12",
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

        login_response = client.post("/api/user/login", json={"username": username, "password": "Secret12"})
        assert login_response.status_code == 200
        assert login_response.get_json()["user"]["displayName"] == "A Test User"
    finally:
        _write_json(USERS_FILE, original_users)


def test_delete_account_flow():
    original_users = _read_json(USERS_FILE)
    app = create_app()
    client = app.test_client()
    username = f"user_{uuid.uuid4().hex[:8]}"
    try:
        register_response = client.post("/api/user/register", json={
            "username": username,
            "password": "Secret12",
            "displayName": "Delete Me",
        })
        assert register_response.status_code == 201

        delete_response = client.delete("/api/user/account")
        assert delete_response.status_code == 200
        assert delete_response.get_json()["deleted"] is True

        me_response = client.get("/api/user/me")
        assert me_response.get_json()["authenticated"] is False

        login_response = client.post("/api/user/login", json={"username": username, "password": "Secret12"})
        assert login_response.status_code == 401
    finally:
        _write_json(USERS_FILE, original_users)


def test_logged_in_data_persists_through_mongodb_path(monkeypatch):
    original_enabled = user_db_service.enabled
    original_users_method = user_db_service.users
    fake_collection = FakeMongoCollection()

    monkeypatch.setattr(user_db_service, "enabled", True)
    monkeypatch.setattr(user_db_service, "users", lambda: fake_collection)

    app = create_app()
    client = app.test_client()
    username = f"user_{uuid.uuid4().hex[:8]}"

    try:
        register_response = client.post("/api/user/register", json={
            "username": username,
            "password": "Secret12",
            "displayName": "Mongo Demo User",
        })
        assert register_response.status_code == 201

        document = fake_collection.find_one({"username": username})
        assert document is not None
        assert document["displayName"] == "Mongo Demo User"
        assert document["passwordHash"] != "Secret12"
        assert document["preferences"]["theme"] == "dark"
        assert document["watchlist"] == []

        preferences_response = client.put("/api/user/preferences", json={"theme": "light", "defaultRange": "3mo"})
        assert preferences_response.status_code == 200

        watchlist_response = client.post("/api/watchlist", json={"symbol": "IBM"})
        assert watchlist_response.status_code == 201

        document = fake_collection.find_one({"username": username})
        assert document["preferences"]["theme"] == "light"
        assert document["preferences"]["defaultRange"] == "3mo"
        assert "IBM" in document["watchlist"]
    finally:
        monkeypatch.setattr(user_db_service, "enabled", original_enabled)
        monkeypatch.setattr(user_db_service, "users", original_users_method)


def test_delete_account_through_mongodb_path(monkeypatch):
    original_enabled = user_db_service.enabled
    original_users_method = user_db_service.users
    fake_collection = FakeMongoCollection()

    monkeypatch.setattr(user_db_service, "enabled", True)
    monkeypatch.setattr(user_db_service, "users", lambda: fake_collection)

    app = create_app()
    client = app.test_client()
    username = f"user_{uuid.uuid4().hex[:8]}"

    try:
        register_response = client.post("/api/user/register", json={
            "username": username,
            "password": "Secret12",
            "displayName": "Mongo Delete User",
        })
        assert register_response.status_code == 201
        assert fake_collection.find_one({"username": username}) is not None

        delete_response = client.delete("/api/user/account")
        assert delete_response.status_code == 200
        assert fake_collection.find_one({"username": username}) is None
    finally:
        monkeypatch.setattr(user_db_service, "enabled", original_enabled)
        monkeypatch.setattr(user_db_service, "users", original_users_method)


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


def test_news_general_falls_back_to_symbol_basket(monkeypatch):
    cache.clear()

    class EmptyGeneralProvider:
        def enabled(self):
            return True

        def news(self, symbol=None, category="general"):
            if symbol:
                return [{
                    "id": f"{symbol}-1",
                    "headline": f"{symbol} update",
                    "summary": "Live market story",
                    "source": "Provider Desk",
                    "url": f"https://example.com/{symbol.lower()}",
                    "datetime": 1778153232,
                }]
            return []

    class DisabledProvider:
        def enabled(self):
            return False

        def news(self, symbol=None, category="general"):
            return []

    monkeypatch.setattr(news_service, "finnhub", EmptyGeneralProvider())
    monkeypatch.setattr(news_service, "alpha_vantage", DisabledProvider())

    payload = news_service.get_news(symbol=None, category="general")

    assert payload["provider"] == "finnhub"
    assert payload["data"]
    assert payload["data"][0]["provider"] == "finnhub"
    assert payload["data"][0]["url"].startswith("https://example.com/")


def _read_json(path):
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path, payload):
    with Path(path).open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


class FakeMongoCollection:
    def __init__(self):
        self.docs = []

    def find(self, query=None, projection=None):
        query = query or {}
        results = [deepcopy(doc) for doc in self.docs if self._matches(doc, query)]
        if projection and projection.get("_id") == 0:
            return [{key: value for key, value in doc.items() if key != "_id"} for doc in results]
        return results

    def find_one(self, query, projection=None):
        for doc in self.docs:
            if self._matches(doc, query):
                result = deepcopy(doc)
                if projection:
                    include_keys = [key for key, value in projection.items() if value and key != "_id"]
                    if include_keys:
                        filtered = {key: result.get(key) for key in include_keys}
                        if projection.get("_id", 1):
                            filtered["_id"] = result.get("_id")
                        return filtered
                    if projection.get("_id") == 0:
                        result.pop("_id", None)
                return result
        return None

    def delete_many(self, _query):
        self.docs = []

    def delete_one(self, query):
        for index, doc in enumerate(self.docs):
            if self._matches(doc, query):
                del self.docs[index]
                return FakeDeleteResult(1)
        return FakeDeleteResult(0)

    def insert_many(self, docs):
        for doc in docs:
            self.insert_one(doc)

    def insert_one(self, doc):
        next_doc = deepcopy(doc)
        next_doc.setdefault("_id", uuid.uuid4().hex)
        self.docs.append(next_doc)

    def update_one(self, query, update, upsert=False):
        for index, doc in enumerate(self.docs):
            if self._matches(doc, query):
                next_doc = deepcopy(doc)
                next_doc.update(deepcopy(update.get("$set", {})))
                for key, value in deepcopy(update.get("$addToSet", {})).items():
                    current = list(next_doc.get(key, []))
                    if value not in current:
                        current.append(value)
                    next_doc[key] = current
                for key, value in deepcopy(update.get("$pull", {})).items():
                    next_doc[key] = [item for item in next_doc.get(key, []) if item != value]
                self.docs[index] = next_doc
                return FakeUpdateResult(1)

        if upsert:
            next_doc = deepcopy(query)
            next_doc.update(deepcopy(update.get("$set", {})))
            self.insert_one(next_doc)
            return FakeUpdateResult(1)

        return FakeUpdateResult(0)

    def _matches(self, doc, query):
        return all(doc.get(key) == value for key, value in query.items())


class FakeUpdateResult:
    def __init__(self, matched_count):
        self.matched_count = matched_count


class FakeDeleteResult:
    def __init__(self, deleted_count):
        self.deleted_count = deleted_count
