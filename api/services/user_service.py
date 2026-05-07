import hashlib
from datetime import datetime, timezone

from config import ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY, PASSWORD_SALT, PREFERENCES_FILE, USERS_FILE
from services.json_store import JsonStore


DEFAULT_PREFERENCES = {
    "theme": "dark",
    "defaultRange": "1mo",
    "refreshInterval": 60,
}


class UserService:
    def __init__(self):
        self.preferences_store = JsonStore(PREFERENCES_FILE, DEFAULT_PREFERENCES)
        self.users_store = JsonStore(USERS_FILE, {"users": []})

    def register(self, username, password, display_name=""):
        username = self._normalize_username(username)
        password = (password or "").strip()
        display_name = (display_name or "").strip()

        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")

        users = self._load_users()
        if self._find_user(users, username):
            raise ValueError("Username already exists")

        user = {
            "username": username,
            "displayName": display_name or username,
            "passwordHash": self._hash_password(username, password),
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "preferences": DEFAULT_PREFERENCES.copy(),
            "watchlist": [],
        }
        users.append(user)
        self._save_users(users)
        return self._public_user(user)

    def authenticate(self, username, password):
        username = self._normalize_username(username)
        user = self._find_user(self._load_users(), username)
        if not user or user.get("passwordHash") != self._hash_password(username, password or ""):
            raise ValueError("Invalid username or password")
        return self._public_user(user)

    def get_user(self, username):
        user = self._find_user(self._load_users(), self._normalize_username(username))
        return self._public_user(user) if user else None

    def get_preferences(self, username=None):
        if username:
            user = self._find_user(self._load_users(), self._normalize_username(username))
            if not user:
                return DEFAULT_PREFERENCES.copy()
            return {**DEFAULT_PREFERENCES, **(user.get("preferences") or {})}
        return {**DEFAULT_PREFERENCES, **self.preferences_store.read()}

    def update_preferences(self, updates, username=None):
        current = self.get_preferences(username=username)
        allowed = {"theme", "defaultRange", "refreshInterval"}
        next_value = {**current, **{key: value for key, value in (updates or {}).items() if key in allowed}}
        if username:
            users = self._load_users()
            user = self._find_user(users, self._normalize_username(username))
            if not user:
                raise ValueError("User not found")
            user["preferences"] = next_value
            self._save_users(users)
        else:
            self.preferences_store.write(next_value)
        return next_value

    def get_watchlist(self, username):
        user = self._require_user(username)
        return user.get("watchlist", [])

    def add_watchlist(self, username, symbol):
        user = self._require_user(username)
        watchlist = user.setdefault("watchlist", [])
        if symbol not in watchlist:
            watchlist.append(symbol)
            self._persist_user(user)
        return watchlist

    def remove_watchlist(self, username, symbol):
        user = self._require_user(username)
        user["watchlist"] = [item for item in user.get("watchlist", []) if item != symbol]
        self._persist_user(user)
        return user["watchlist"]

    def api_key_status(self):
        return {
            "alphaVantage": bool(ALPHA_VANTAGE_API_KEY),
            "finnhub": bool(FINNHUB_API_KEY),
            "yahooFinance": True,
        }

    def _load_users(self):
        return self.users_store.read().get("users", [])

    def _save_users(self, users):
        self.users_store.write({"users": users})

    def _find_user(self, users, username):
        return next((user for user in users if user.get("username") == username), None)

    def _require_user(self, username):
        username = self._normalize_username(username)
        users = self._load_users()
        user = self._find_user(users, username)
        if not user:
            raise ValueError("User not found")
        return user

    def _persist_user(self, updated_user):
        users = self._load_users()
        for index, user in enumerate(users):
            if user.get("username") == updated_user.get("username"):
                users[index] = updated_user
                self._save_users(users)
                return
        raise ValueError("User not found")

    def _hash_password(self, username, password):
        seed = f"{PASSWORD_SALT}:{username}".encode("utf-8")
        return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), seed, 120000).hex()

    def _normalize_username(self, username):
        return (username or "").strip().lower()

    def _public_user(self, user):
        if not user:
            return None
        return {
            "username": user.get("username"),
            "displayName": user.get("displayName") or user.get("username"),
            "createdAt": user.get("createdAt"),
        }


user_service = UserService()
