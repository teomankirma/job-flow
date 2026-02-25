from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database import get_session
from app.main import app
from tests.conftest import override_session


@pytest.mark.asyncio
class TestMetrics:
    async def test_returns_all_fields(self, client, fake_redis):
        mock_session = AsyncMock()
        mock_row = MagicMock()
        mock_row.total_jobs = 10
        mock_row.active_jobs = 2
        mock_row.completed_jobs = 5
        mock_row.failed_jobs = 2
        mock_row.dead_letter_jobs = 1

        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_session.execute = AsyncMock(return_value=mock_result)

        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.get("/metrics")
        assert response.status_code == 200
        data = response.json()

        assert data["total_jobs"] == 10
        assert data["active_jobs"] == 2
        assert data["completed_jobs"] == 5
        assert data["failed_jobs"] == 2
        assert data["dead_letter_jobs"] == 1
        assert data["queue_length"] == 0
        assert data["retry_queue_length"] == 0
        assert data["dlq_length"] == 0

    async def test_reflects_redis_queue_lengths(self, client, fake_redis):
        # Populate fake Redis queues
        await fake_redis.rpush("job_queue", "job-1", "job-2")
        await fake_redis.zadd("retry_queue", {"job-3": 100.0})
        await fake_redis.rpush("dead_letter_queue", "job-4")

        mock_session = AsyncMock()
        mock_row = MagicMock()
        mock_row.total_jobs = 4
        mock_row.active_jobs = 0
        mock_row.completed_jobs = 0
        mock_row.failed_jobs = 0
        mock_row.dead_letter_jobs = 1

        mock_result = MagicMock()
        mock_result.one.return_value = mock_row
        mock_session.execute = AsyncMock(return_value=mock_result)

        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.get("/metrics")
        assert response.status_code == 200
        data = response.json()

        assert data["queue_length"] == 2
        assert data["retry_queue_length"] == 1
        assert data["dlq_length"] == 1
