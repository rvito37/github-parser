import time
from typing import Any


class TTLCache:
    def __init__(self, default_ttl: int = 300):
        self._cache: dict[str, tuple[Any, float]] = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Any | None:
        if key not in self._cache:
            return None
        value, expires_at = self._cache[key]
        if time.time() > expires_at:
            del self._cache[key]
            return None
        return value

    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        expires_at = time.time() + (ttl if ttl is not None else self._default_ttl)
        self._cache[key] = (value, expires_at)

    def clear(self) -> None:
        self._cache.clear()
