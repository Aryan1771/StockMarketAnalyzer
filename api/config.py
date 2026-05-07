import os
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


BASE_DIR = Path(__file__).resolve().parent
STORAGE_DIR = BASE_DIR / "storage"
WATCHLIST_FILE = STORAGE_DIR / "watchlist.json"
PREFERENCES_FILE = STORAGE_DIR / "preferences.json"
USERS_FILE = STORAGE_DIR / "users.json"
MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "stockmarketanalyzer")

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")

SECRET_KEY = os.getenv("SECRET_KEY", "stockmarketanalyzer-dev-secret")
PASSWORD_SALT = os.getenv("PASSWORD_SALT", "stockmarketanalyzer-dev-salt")
FRONTEND_ORIGINS = [
    item.strip()
    for item in os.getenv("FRONTEND_ORIGINS", "http://127.0.0.1:5173,http://localhost:5173").split(",")
    if item.strip()
]
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true"
SESSION_COOKIE_SAMESITE = os.getenv("SESSION_COOKIE_SAMESITE", "Lax")
FRONTEND_APP_URL = os.getenv("FRONTEND_APP_URL", FRONTEND_ORIGINS[0] if FRONTEND_ORIGINS else "http://127.0.0.1:5173")

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
MICROSOFT_CLIENT_ID = os.getenv("MICROSOFT_CLIENT_ID", "")
MICROSOFT_CLIENT_SECRET = os.getenv("MICROSOFT_CLIENT_SECRET", "")
MICROSOFT_TENANT_ID = os.getenv("MICROSOFT_TENANT_ID", "common")

DEFAULT_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "120"))
