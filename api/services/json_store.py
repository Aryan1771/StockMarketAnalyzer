import json
from pathlib import Path


class JsonStore:
    def __init__(self, path, default_value):
        self.path = Path(path)
        self.default_value = default_value
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.write(default_value)

    def read(self):
        try:
            with self.path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except (json.JSONDecodeError, OSError):
            return self.default_value

    def write(self, value):
        with self.path.open("w", encoding="utf-8") as handle:
            json.dump(value, handle, indent=2)
        return value
