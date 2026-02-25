import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import get_session
from app.main import app
from app.redis_client import get_redis


class FakeRedis:
    """Minimal in-memory Redis fake for testing."""

    def __init__(self):
        self._lists: dict[str, list] = {}
        self._zsets: dict[str, dict] = {}

    async def rpush(self, key: str, *values):
        self._lists.setdefault(key, []).extend(values)
        return len(self._lists[key])

    async def llen(self, key: str) -> int:
        return len(self._lists.get(key, []))

    async def zcard(self, key: str) -> int:
        return len(self._zsets.get(key, {}))

    async def zadd(self, key: str, mapping: dict):
        self._zsets.setdefault(key, {}).update(mapping)

    async def zremrangebyscore(self, key, min_score, max_score):
        return 0

    def pipeline(self):
        return FakePipeline(self)


class FakePipeline:
    def __init__(self, redis: FakeRedis):
        self._redis = redis
        self._commands: list[tuple] = []

    def zremrangebyscore(self, key, min_s, max_s):
        self._commands.append(("zremrangebyscore", key, min_s, max_s))
        return self

    def zadd(self, key, mapping):
        self._commands.append(("zadd", key, mapping))
        return self

    def zcard(self, key):
        self._commands.append(("zcard", key))
        return self

    def expire(self, key, ttl):
        self._commands.append(("expire", key, ttl))
        return self

    async def execute(self):
        results = []
        for cmd in self._commands:
            if cmd[0] == "zremrangebyscore":
                results.append(0)
            elif cmd[0] == "zadd":
                await self._redis.zadd(cmd[1], cmd[2])
                results.append(1)
            elif cmd[0] == "zcard":
                results.append(await self._redis.zcard(cmd[1]))
            elif cmd[0] == "expire":
                results.append(True)
        return results


def make_job(**kwargs):
    """Factory for creating mock Job instances for testing."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    defaults = {
        "id": uuid.uuid4(),
        "type": "email.send",
        "payload": {"to": "test@example.com"},
        "status": "pending",
        "attempts": 0,
        "max_attempts": 3,
        "error_message": None,
        "idempotency_key": None,
        "created_at": now,
        "updated_at": now,
    }
    defaults.update(kwargs)
    job = MagicMock()
    for k, v in defaults.items():
        setattr(job, k, v)
    return job


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest_asyncio.fixture
async def client(fake_redis):
    """AsyncClient wired to the FastAPI app with mocked dependencies."""

    async def override_get_redis():
        return fake_redis

    # Default mock session — individual tests can override further
    default_session = AsyncMock()

    async def override_get_session():
        yield default_session

    app.dependency_overrides[get_redis] = override_get_redis
    app.dependency_overrides[get_session] = override_get_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c

    app.dependency_overrides.clear()


def mock_session_with_result(result_value):
    """Create a mock session that returns a single result."""
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = result_value
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()
    return mock_session


def override_session(mock_session):
    """Create a dependency override for get_session."""

    async def _override():
        yield mock_session

    return _override
