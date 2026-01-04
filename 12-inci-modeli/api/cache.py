"""
Caching System for 12. İnci Modeli
Redis-based caching for improved performance
"""

import json
import hashlib
from typing import Optional, Any
import logging
from datetime import timedelta
import os

logger = logging.getLogger(__name__)

# Try to import Redis, but make it optional
try:
    import aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("aioredis not installed. Caching disabled.")


class CacheManager:
    """
    Cache manager for emotion detection results
    Uses Redis for distributed caching with fallback to in-memory
    """

    def __init__(self):
        self.redis = None
        self.enabled = False
        self.in_memory_cache = {}  # Fallback cache
        self.max_memory_items = 1000

    async def connect(self):
        """Connect to Redis"""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, using in-memory cache")
            return

        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            self.redis = await aioredis.create_redis_pool(redis_url)
            self.enabled = True
            logger.info(f"Connected to Redis: {redis_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            logger.warning("Falling back to in-memory cache")
            self.enabled = False

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()
            logger.info("Disconnected from Redis")

    def _generate_cache_key(self, prefix: str, data: Any) -> str:
        """Generate cache key from data"""
        # Create hash of data
        data_str = json.dumps(data, sort_keys=True)
        hash_obj = hashlib.md5(data_str.encode())
        return f"{prefix}:{hash_obj.hexdigest()}"

    async def get(self, key: str) -> Optional[dict]:
        """Get value from cache"""
        try:
            if self.redis and self.enabled:
                # Redis cache
                value = await self.redis.get(key)
                if value:
                    logger.debug(f"Cache HIT: {key}")
                    return json.loads(value.decode())
                else:
                    logger.debug(f"Cache MISS: {key}")
                    return None
            else:
                # In-memory cache
                if key in self.in_memory_cache:
                    logger.debug(f"Memory cache HIT: {key}")
                    return self.in_memory_cache[key]
                else:
                    logger.debug(f"Memory cache MISS: {key}")
                    return None

        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None

    async def set(
        self,
        key: str,
        value: dict,
        expire_seconds: int = 3600
    ):
        """Set value in cache with expiration"""
        try:
            if self.redis and self.enabled:
                # Redis cache
                await self.redis.setex(
                    key,
                    expire_seconds,
                    json.dumps(value)
                )
                logger.debug(f"Cache SET: {key} (expires in {expire_seconds}s)")
            else:
                # In-memory cache with size limit
                if len(self.in_memory_cache) >= self.max_memory_items:
                    # Remove oldest item (simple FIFO)
                    oldest_key = next(iter(self.in_memory_cache))
                    del self.in_memory_cache[oldest_key]

                self.in_memory_cache[key] = value
                logger.debug(f"Memory cache SET: {key}")

        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")

    async def delete(self, key: str):
        """Delete value from cache"""
        try:
            if self.redis and self.enabled:
                await self.redis.delete(key)
            else:
                self.in_memory_cache.pop(key, None)

            logger.debug(f"Cache DELETE: {key}")

        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")

    async def clear(self):
        """Clear all cache"""
        try:
            if self.redis and self.enabled:
                await self.redis.flushdb()
            else:
                self.in_memory_cache.clear()

            logger.info("Cache cleared")

        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")

    async def get_emotion_cache(self, text: str, language: str) -> Optional[dict]:
        """Get cached emotion detection result"""
        cache_key = self._generate_cache_key(
            "emotion",
            {"text": text, "lang": language}
        )
        return await self.get(cache_key)

    async def set_emotion_cache(
        self,
        text: str,
        language: str,
        result: dict,
        expire_seconds: int = 3600
    ):
        """Cache emotion detection result"""
        cache_key = self._generate_cache_key(
            "emotion",
            {"text": text, "lang": language}
        )
        await self.set(cache_key, result, expire_seconds)

    async def get_ai_response_cache(
        self,
        text: str,
        emotions: list
    ) -> Optional[str]:
        """Get cached AI response"""
        cache_key = self._generate_cache_key(
            "ai_response",
            {"text": text, "emotions": [e.type for e in emotions]}
        )
        cached = await self.get(cache_key)
        return cached.get("response") if cached else None

    async def set_ai_response_cache(
        self,
        text: str,
        emotions: list,
        response: str,
        expire_seconds: int = 1800  # 30 minutes
    ):
        """Cache AI response"""
        cache_key = self._generate_cache_key(
            "ai_response",
            {"text": text, "emotions": [e.type for e in emotions]}
        )
        await self.set(
            cache_key,
            {"response": response},
            expire_seconds
        )


# Global cache instance
cache = CacheManager()


# ============================================
# Usage in main.py
# ============================================

"""
Add to main.py startup:

@app.on_event("startup")
async def startup():
    await cache.connect()

@app.on_event("shutdown")
async def shutdown():
    await cache.disconnect()


In emotion analysis endpoint:

# Check cache
cached = await cache.get_emotion_cache(request.text, request.language)
if cached:
    return cached

# ... perform detection ...

# Cache result
await cache.set_emotion_cache(
    request.text,
    request.language,
    response_data
)
"""
