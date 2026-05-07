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

DEFAULT_SYMBOLS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "120"))
