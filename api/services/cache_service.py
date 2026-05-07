import time


class TTLCache:
    def __init__(self):
        self._items = {}

    def get(self, key):
        item = self._items.get(key)
        if not item:
            return None

        expires_at, value = item
        if expires_at < time.time():
            self._items.pop(key, None)
            return None

        return value

    def set(self, key, value, ttl_seconds):
        self._items[key] = (time.time() + ttl_seconds, value)

    def clear(self):
        self._items.clear()


cache = TTLCache()
