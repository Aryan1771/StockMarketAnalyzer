import hashlib
import re
from datetime import datetime, timezone

from config import ALPHA_VANTAGE_API_KEY, FINNHUB_API_KEY, PASSWORD_SALT, PREFERENCES_FILE, USERS_FILE
from services.db_service import db_service
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
        self._validate_password(password)

        user = {
            "username": username,
            "displayName": display_name or username,
            "passwordHash": self._hash_password(username, password),
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "preferences": DEFAULT_PREFERENCES.copy(),
            "watchlist": [],
        }

        if db_service.enabled:
            collection = db_service.users()
            if collection.find_one({"username": username}):
                raise ValueError("Username already exists")
            collection.insert_one(user)
            return self._public_user(user)

        users = self._load_users()
        if self._find_user(users, username):
            raise ValueError("Username already exists")
        users.append(user)
        self._save_users(users)
        return self._public_user(user)

    def get_or_create_oauth_user(self, provider, provider_user_id, email="", display_name=""):
        provider = (provider or "").strip().lower()
        provider_user_id = (provider_user_id or "").strip()
        email = (email or "").strip().lower()
        display_name = (display_name or "").strip()

        if db_service.enabled:
            users = db_service.users()
            user = users.find_one({"authProvider": provider, "providerUserId": provider_user_id})
            if not user and email:
                user = users.find_one({"email": email})
                if user:
                    users.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"authProvider": provider, "providerUserId": provider_user_id, "displayName": display_name or user.get("displayName")}},
                    )
                    user = users.find_one({"_id": user["_id"]})
            if user:
                return self._public_user(user)

            username = self._generate_available_username(display_name or email or provider_user_id)
            user_doc = {
                "username": username,
                "displayName": display_name or username,
                "email": email or None,
                "passwordHash": None,
                "authProvider": provider,
                "providerUserId": provider_user_id,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "preferences": DEFAULT_PREFERENCES.copy(),
                "watchlist": [],
            }
            users.insert_one(user_doc)
            return self._public_user(user_doc)

        users = self._load_users()
        user = next((item for item in users if item.get("authProvider") == provider and item.get("providerUserId") == provider_user_id), None)
        if user:
            return self._public_user(user)

        username = self._generate_available_username(display_name or email or provider_user_id)
        user = {
            "username": username,
            "displayName": display_name or username,
            "email": email or None,
            "passwordHash": None,
            "authProvider": provider,
            "providerUserId": provider_user_id,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "preferences": DEFAULT_PREFERENCES.copy(),
            "watchlist": [],
        }
        users.append(user)
        self._save_users(users)
        return self._public_user(user)

    def authenticate(self, username, password):
        username = self._normalize_username(username)
        if db_service.enabled:
            user = db_service.users().find_one({"username": username}, {"_id": 0})
        else:
            user = self._find_user(self._load_users(), username)
        if not user or user.get("passwordHash") != self._hash_password(username, password or ""):
            raise ValueError("Invalid username or password")
        return self._public_user(user)

    def get_user(self, username):
        username = self._normalize_username(username)
        if db_service.enabled:
            user = db_service.users().find_one({"username": username}, {"_id": 0})
        else:
            user = self._find_user(self._load_users(), username)
        return self._public_user(user) if user else None

    def delete_user(self, username):
        username = self._normalize_username(username)
        if db_service.enabled:
            result = db_service.users().delete_one({"username": username})
            if not result.deleted_count:
                raise ValueError("User not found")
            return {"deleted": True}

        users = self._load_users()
        next_users = [user for user in users if user.get("username") != username]
        if len(next_users) == len(users):
            raise ValueError("User not found")
        self._save_users(next_users)
        return {"deleted": True}

    def get_preferences(self, username=None):
        if username:
            username = self._normalize_username(username)
            if db_service.enabled:
                user = db_service.users().find_one({"username": username}, {"_id": 0})
            else:
                user = self._find_user(self._load_users(), username)
            if not user:
                return DEFAULT_PREFERENCES.copy()
            return {**DEFAULT_PREFERENCES, **(user.get("preferences") or {})}
        if db_service.enabled:
            return DEFAULT_PREFERENCES.copy()
        return {**DEFAULT_PREFERENCES, **self.preferences_store.read()}

    def update_preferences(self, updates, username=None):
        current = self.get_preferences(username=username)
        allowed = {"theme", "defaultRange", "refreshInterval"}
        next_value = {**current, **{key: value for key, value in (updates or {}).items() if key in allowed}}
        if username:
            username = self._normalize_username(username)
            if db_service.enabled:
                result = db_service.users().update_one({"username": username}, {"$set": {"preferences": next_value}})
                if not result.matched_count:
                    raise ValueError("User not found")
            else:
                users = self._load_users()
                user = self._find_user(users, username)
                if not user:
                    raise ValueError("User not found")
                user["preferences"] = next_value
                self._save_users(users)
        elif db_service.enabled:
            return next_value
        else:
            self.preferences_store.write(next_value)
        return next_value

    def get_watchlist(self, username):
        username = self._normalize_username(username)
        if db_service.enabled:
            user = db_service.users().find_one({"username": username}, {"_id": 0, "watchlist": 1})
            if not user:
                raise ValueError("User not found")
            return user.get("watchlist", [])
        user = self._require_user(username)
        return user.get("watchlist", [])

    def add_watchlist(self, username, symbol):
        username = self._normalize_username(username)
        if db_service.enabled:
            result = db_service.users().update_one({"username": username}, {"$addToSet": {"watchlist": symbol}})
            if not result.matched_count:
                raise ValueError("User not found")
            return self.get_watchlist(username)

        user = self._require_user(username)
        watchlist = user.setdefault("watchlist", [])
        if symbol not in watchlist:
            watchlist.append(symbol)
            self._persist_user(user)
        return watchlist

    def remove_watchlist(self, username, symbol):
        username = self._normalize_username(username)
        if db_service.enabled:
            result = db_service.users().update_one({"username": username}, {"$pull": {"watchlist": symbol}})
            if not result.matched_count:
                raise ValueError("User not found")
            return self.get_watchlist(username)

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
        if db_service.enabled:
            return list(db_service.users().find({}, {"_id": 0}))
        return self.users_store.read().get("users", [])

    def _save_users(self, users):
        if db_service.enabled:
            collection = db_service.users()
            collection.delete_many({})
            if users:
                collection.insert_many(users)
            return
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
        if db_service.enabled:
            db_service.users().update_one(
                {"username": updated_user.get("username")},
                {"$set": {
                    "displayName": updated_user.get("displayName"),
                    "email": updated_user.get("email"),
                    "passwordHash": updated_user.get("passwordHash"),
                    "authProvider": updated_user.get("authProvider"),
                    "providerUserId": updated_user.get("providerUserId"),
                    "createdAt": updated_user.get("createdAt"),
                    "preferences": updated_user.get("preferences", DEFAULT_PREFERENCES.copy()),
                    "watchlist": updated_user.get("watchlist", []),
                }},
                upsert=True,
            )
            return
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

    def _validate_password(self, password):
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[a-z]", password):
            raise ValueError("Password must include at least one lowercase letter")
        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must include at least one uppercase letter")
        if not re.search(r"\d", password):
            raise ValueError("Password must include at least one number")

    def _generate_available_username(self, raw_value):
        base = re.sub(r"[^a-z0-9]+", "", (raw_value or "user").lower())[:18] or "user"
        username = base
        counter = 1
        users = self._load_users()
        while self._find_user(users, username):
            counter += 1
            username = f"{base[:14]}{counter}"
        return username

    def _public_user(self, user):
        if not user:
            return None
        return {
            "username": user.get("username"),
            "displayName": user.get("displayName") or user.get("username"),
            "createdAt": user.get("createdAt"),
            "authProvider": user.get("authProvider") or "password",
            "email": user.get("email"),
        }


user_service = UserService()
