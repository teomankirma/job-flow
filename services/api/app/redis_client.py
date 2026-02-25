import os

from redis.asyncio import Redis

redis_client: Redis | None = None


def init_redis() -> None:
    global redis_client
    url = os.environ["REDIS_URL"]
    redis_client = Redis.from_url(url, decode_responses=True)


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


async def get_redis() -> Redis:
    return redis_client
