import os
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.redis_client import redis_client


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis sliding-window rate limiter for POST requests."""

    def __init__(self, app, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = int(os.getenv("RATE_LIMIT_MAX", str(max_requests)))
        self.window_seconds = int(os.getenv("RATE_LIMIT_WINDOW", str(window_seconds)))

    async def dispatch(self, request: Request, call_next) -> Response:
        if request.method != "POST":
            return await call_next(request)

        if redis_client is None:
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        key = f"rate_limit:{client_ip}"
        now = time.time()
        window_start = now - self.window_seconds

        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, window_start)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, self.window_seconds)
        results = await pipe.execute()

        request_count = results[2]

        if request_count > self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests"},
                headers={"Retry-After": str(self.window_seconds)},
            )

        return await call_next(request)
