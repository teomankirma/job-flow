import os

from redis.asyncio import Redis
from redis.exceptions import ConnectionError, TimeoutError

redis_client: Redis | None = None


def init_redis() -> None:
    global redis_client
    url = os.environ["REDIS_URL"]
    redis_client = Redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_error=[ConnectionError, TimeoutError],
    )


async def close_redis() -> None:
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
