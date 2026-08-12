import json
import os
import uuid
from threading import Lock


class PendingStore:
    """待创建队列持久化（列表结构，按添加顺序排序）"""

    def __init__(self, path: str):
        self.path = path
        self.lock = Lock()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)

    def _read(self):
        with open(self.path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def all(self) -> list[dict]:
        with self.lock:
            return self._read()

    def add(self, item: dict) -> str:
        item_id = uuid.uuid4().hex[:12]
        entry = {
            "id": item_id,
            "name": item.get("name", ""),
            "server_type": item.get("server_type", ""),
            "location": item.get("location", ""),
            "image": item.get("image", "debian-12"),
            "primary_ip_id": item.get("primary_ip_id"),
            "primary_ipv6_id": item.get("primary_ipv6_id"),
            "status": "pending",  # pending | creating | created | failed | cancelled
            "error": None,
            "server_id": None,
            "created_at": None,
            "updated_at": None,
        }
        with self.lock:
            data = self._read()
            entry["created_at"] = _now_ts()
            data.append(entry)
            self._write(data)
        return item_id

    def get(self, item_id: str) -> dict | None:
        with self.lock:
            data = self._read()
            for e in data:
                if e.get("id") == item_id:
                    return e
        return None

    def update(self, item_id: str, **kwargs):
        with self.lock:
            data = self._read()
            for e in data:
                if e.get("id") == item_id:
                    e.update(kwargs)
                    e["updated_at"] = _now_ts()
                    break
            self._write(data)

    def delete(self, item_id: str):
        with self.lock:
            data = self._read()
            data = [e for e in data if e.get("id") != item_id]
            self._write(data)

    def pending_items(self) -> list[dict]:
        """返回所有待处理（pending）的条目"""
        with self.lock:
            return [e for e in self._read() if e.get("status") == "pending"]


def _now_ts() -> int:
    import datetime as dt
    return int(dt.datetime.utcnow().timestamp())