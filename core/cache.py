# core/cache.py — LRU Cache Layer

import time
from collections import OrderedDict
from typing import Any, Optional, Callable


class LRUCache:
    """
    Least Recently Used Cache สำหรับเก็บผลลัพธ์ของ Math / Search tools
    """

    def __init__(self, maxsize: int = 128, ttl: Optional[float] = None):
        self._maxsize = maxsize
        self._ttl = ttl  # seconds; None = ไม่หมดอายุ
        self._store: OrderedDict[str, tuple] = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        if key not in self._store:
            self._misses += 1
            return None
        value, expires = self._store[key]
        if expires is not None and now > expires:
            del self._store[key]
            self._misses += 1
            return None
        self._store.move_to_end(key)
        self._hits += 1
        return value

    def set(self, key: str, value: Any):
        now = time.time()
        expires = (now + self._ttl) if self._ttl else None
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = (value, expires)
        while len(self._store) > self._maxsize:
            self._store.popitem(last=False)

    def clear(self):
        self._store.clear()
        self._hits = 0
        self._misses = 0

    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = round(self._hits / total, 4) if total > 0 else 0.0
        return {
            "size": len(self._store),
            "maxsize": self._maxsize,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate,
        }

    def __contains__(self, key: str) -> bool:
        return self.get(key) is not None


# Global cache instance สำหรับใช้ทั่วทั้ง tools
_global_cache = LRUCache(maxsize=128, ttl=None)


def cached(cache_key_prefix: str = ""):
    """
    Decorator: cache ผลลัพธ์ของฟังก์ชัน tool handler
    ใช้ key = prefix + inp (ข้อความนำเข้า)
    """
    def decorator(func: Callable):
        def wrapper(action: str, inp: str, entities: list):
            key = f"{cache_key_prefix or func.__name__}:{inp.strip()}"
            cached_result = _global_cache.get(key)
            if cached_result is not None:
                return {**cached_result, "cached": True}
            result = func(action, inp, entities)
            if result.get("status") == "success":
                _global_cache.set(key, result)
            return result
        return wrapper
    return decorator
