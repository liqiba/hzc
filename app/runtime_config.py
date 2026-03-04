import json
import os
from threading import Lock


class RuntimeConfig:
    def __init__(self, path: str):
        self.path = path
        self.lock = Lock()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _read(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get(self):
        with self.lock:
            return self._read()

    def update(self, payload: dict):
        with self.lock:
            data = self._read()
            data.update(payload)
            self._write(data)
            return data
