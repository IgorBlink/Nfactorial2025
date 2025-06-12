import json
import redis.asyncio as redis
from typing import Any, Optional
from .config import settings

class RedisClient:
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Initialize Redis connection"""
        if not self.redis_client:
            self.redis_client = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set a value in Redis with optional TTL"""
        await self.connect()
        ttl = ttl or settings.cache_ttl
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return await self.redis_client.setex(key, ttl, value)
    
    async def get(self, key: str) -> Optional[Any]:
        """Get a value from Redis"""
        await self.connect()
        value = await self.redis_client.get(key)
        
        if value is None:
            return None
        
        # Try to parse as JSON, fallback to string
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    async def delete(self, key: str) -> bool:
        """Delete a key from Redis"""
        await self.connect()
        return bool(await self.redis_client.delete(key))
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists in Redis"""
        await self.connect()
        return bool(await self.redis_client.exists(key))
    
    async def clear_pattern(self, pattern: str) -> int:
        """Delete all keys matching a pattern"""
        await self.connect()
        keys = await self.redis_client.keys(pattern)
        if keys:
            return await self.redis_client.delete(*keys)
        return 0
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a numeric value"""
        await self.connect()
        return await self.redis_client.incrby(key, amount)

# Global Redis client instance
redis_client = RedisClient() 