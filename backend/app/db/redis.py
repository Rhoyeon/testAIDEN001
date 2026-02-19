"""Redis connection management with fakeredis fallback."""

from __future__ import annotations
import redis.asyncio as aioredis

from app.config import settings

redis_client: aioredis.Redis | None = None


async def init_redis() -> None:
    """Initialize Redis connection pool.

    Falls back to fakeredis when USE_SQLITE=true (Docker-free dev mode)
    or when the real Redis server is unreachable.
    """
    global redis_client

    if settings.use_sqlite:
        # Use fakeredis for Docker-free development
        try:
            import fakeredis.aioredis as fakeredis_aio
            redis_client = fakeredis_aio.FakeRedis(decode_responses=True)
            print("[DEV] Using fakeredis (in-memory) - no Redis server required")
            return
        except ImportError:
            print("[DEV] fakeredis not installed, trying real Redis...")

    redis_client = aioredis.from_url(
        settings.redis_url,
        decode_responses=True,
        max_connections=20,
    )

    # Verify connectivity
    try:
        await redis_client.ping()
    except Exception as e:
        # Fallback to fakeredis if real Redis is unreachable
        try:
            import fakeredis.aioredis as fakeredis_aio
            redis_client = fakeredis_aio.FakeRedis(decode_responses=True)
            print(f"[DEV] Redis unreachable ({e}), using fakeredis fallback")
        except ImportError:
            raise RuntimeError(
                f"Redis connection failed ({e}) and fakeredis is not installed. "
                f"Install fakeredis: pip install fakeredis[lua]"
            )


async def close_redis() -> None:
    """Close Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


def get_redis() -> aioredis.Redis:
    """Get the Redis client instance."""
    if redis_client is None:
        raise RuntimeError("Redis client not initialized. Call init_redis() first.")
    return redis_client
