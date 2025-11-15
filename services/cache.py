"""
Простое in-memory кэширование с TTL
"""
import time
from typing import Optional, Any, Dict
from datetime import datetime, timedelta


class Cache:
    """Простой кэш с TTL (Time To Live)"""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша, если оно не истекло"""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        expires_at = entry.get("expires_at")
        
        if expires_at and time.time() > expires_at:
            # Истекло, удаляем
            del self._cache[key]
            return None
        
        return entry.get("value")
    
    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """
        Сохраняет значение в кэш с TTL
        
        Args:
            key: Ключ кэша
            value: Значение для кэширования
            ttl: Time to live в секундах (по умолчанию 5 минут)
        """
        expires_at = time.time() + ttl
        self._cache[key] = {
            "value": value,
            "expires_at": expires_at,
            "created_at": time.time()
        }
    
    def delete(self, key: str) -> None:
        """Удаляет значение из кэша"""
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Очищает весь кэш"""
        self._cache.clear()
    
    def cleanup_expired(self) -> None:
        """Удаляет все истекшие записи"""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.get("expires_at") and entry["expires_at"] < now
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def size(self) -> int:
        """Возвращает количество записей в кэше"""
        return len(self._cache)


# Глобальный экземпляр кэша
_cache = Cache()


def get_cache() -> Cache:
    """Получает глобальный экземпляр кэша"""
    return _cache

