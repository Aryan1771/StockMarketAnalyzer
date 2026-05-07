from config import DEFAULT_SYMBOLS, WATCHLIST_FILE
from services.json_store import JsonStore
from services.user_service import user_service
from utils import normalize_symbol


class WatchlistService:
    def __init__(self):
        self.store = JsonStore(WATCHLIST_FILE, {"symbols": DEFAULT_SYMBOLS[:3]})

    def list_symbols(self, username=None):
        if username:
            return user_service.get_watchlist(username)
        payload = self.store.read()
        return payload.get("symbols", [])

    def add(self, symbol, username=None):
        symbol = normalize_symbol(symbol)
        if not symbol:
            raise ValueError("Symbol is required")
        if username:
            return user_service.add_watchlist(username, symbol)
        symbols = self.list_symbols()
        if symbol not in symbols:
            symbols.append(symbol)
            self.store.write({"symbols": symbols})
        return symbols

    def remove(self, symbol, username=None):
        symbol = normalize_symbol(symbol)
        if username:
            return user_service.remove_watchlist(username, symbol)
        symbols = [item for item in self.list_symbols() if item != symbol]
        self.store.write({"symbols": symbols})
        return symbols


watchlist_service = WatchlistService()
