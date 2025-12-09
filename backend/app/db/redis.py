import redis.asyncio as redis
from app.config import get_settings

settings = get_settings()


class RedisClient:
    """Redis connection manager"""

    client: redis.Redis = None


redis_client = RedisClient()


async def connect_to_redis():
    """Connect to Redis"""
    redis_client.client = await redis.from_url(
        settings.REDIS_URL,
        db=settings.REDIS_DB,
        encoding="utf-8",
        decode_responses=True
    )
    print("✅ Connected to Redis")


async def close_redis_connection():
    """Close Redis connection"""
    if redis_client.client:
        await redis_client.client.close()
        print("✅ Closed Redis connection")


async def get_redis() -> redis.Redis:
    """Get Redis client instance"""
    return redis_client.client
