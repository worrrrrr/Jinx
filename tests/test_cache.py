"""Unit tests สำหรับ core/cache.py LRUCache"""

import time
from core.cache import LRUCache, _global_cache


class TestLRUCache:
    def test_get_set(self):
        c = LRUCache(maxsize=10)
        c.set("a", 1)
        assert c.get("a") == 1

    def test_get_miss(self):
        c = LRUCache(maxsize=10)
        assert c.get("nonexistent") is None

    def test_eviction(self):
        c = LRUCache(maxsize=2)
        c.set("a", 1)
        c.set("b", 2)
        c.set("c", 3)  # ควร evict "a"
        assert c.get("a") is None
        assert c.get("b") == 2
        assert c.get("c") == 3

    def test_lru_reorder(self):
        c = LRUCache(maxsize=2)
        c.set("a", 1)
        c.set("b", 2)
        c.get("a")  # "a" ถูกใช้ -> เลื่อนท้าย
        c.set("c", 3)  # ควร evict "b" (ไม่ได้ใช้)
        assert c.get("a") == 1
        assert c.get("b") is None
        assert c.get("c") == 3

    def test_ttl_expiry(self):
        c = LRUCache(maxsize=10, ttl=0.1)
        c.set("a", 1)
        assert c.get("a") == 1
        time.sleep(0.15)
        assert c.get("a") is None

    def test_clear(self):
        c = LRUCache(maxsize=10)
        c.set("a", 1)
        c.clear()
        assert c.get("a") is None
        assert c.stats()["hits"] == 0

    def test_stats(self):
        c = LRUCache(maxsize=10)
        c.get("miss1")  # miss
        c.get("miss2")  # miss
        c.set("hit1", 1)
        c.get("hit1")    # hit
        s = c.stats()
        assert s["hits"] == 1
        assert s["misses"] == 2
        assert s["size"] == 1
        assert 0 < s["hit_rate"] < 1

    def test_contains(self):
        c = LRUCache(maxsize=10)
        c.set("a", 1)
        assert "a" in c
        assert "b" not in c

    def test_global_cache(self):
        assert isinstance(_global_cache, LRUCache)
