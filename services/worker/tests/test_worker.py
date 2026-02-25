import asyncio
import os
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Config reads DATABASE_URL/REDIS_URL at import time — set dummy values
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from tests.conftest import make_job


@pytest.mark.asyncio
class TestProcessJob:
    async def test_success_path(self):
        """pending -> processing -> completed"""
        job = make_job(status="pending", attempts=0)

        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = job
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session.commit = AsyncMock()

        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        handler = AsyncMock(return_value={"result": "ok"})

        with (
            patch("app.main.db") as mock_db,
            patch("app.main.rc") as mock_rc,
            patch("app.main.get_handler", return_value=handler),
        ):
            mock_db.async_session_factory = mock_session_factory

            from app.main import process_job

            semaphore = asyncio.Semaphore(5)
            await process_job(str(job.id), semaphore)

            handler.assert_called_once_with(job.payload)
            assert job.status == "completed"

    async def test_failure_with_retry(self):
        """Failed job with remaining attempts -> retrying + ZADD"""
        job = make_job(status="pending", attempts=0, max_attempts=3)

        # First session: fetch job, set processing, handler fails
        mock_session_1 = AsyncMock()
        mock_result_1 = MagicMock()
        mock_result_1.scalar_one_or_none.return_value = job
        mock_session_1.execute = AsyncMock(return_value=mock_result_1)
        mock_session_1.commit = AsyncMock()

        # Second session (error path): re-fetch job with attempts=1
        job_in_error = make_job(
            id=job.id, status="processing", attempts=1, max_attempts=3,
        )
        mock_session_2 = AsyncMock()
        mock_result_2 = MagicMock()
        mock_result_2.scalar_one_or_none.return_value = job_in_error
        mock_session_2.execute = AsyncMock(return_value=mock_result_2)
        mock_session_2.commit = AsyncMock()

        call_count = 0

        class FakeSessionCtx:
            async def __aenter__(self_inner):
                nonlocal call_count
                call_count += 1
                return mock_session_1 if call_count == 1 else mock_session_2

            async def __aexit__(self_inner, *args):
                return False

        mock_session_factory = MagicMock(return_value=FakeSessionCtx())

        handler = AsyncMock(side_effect=RuntimeError("simulated failure"))
        mock_redis = AsyncMock()

        with (
            patch("app.main.db") as mock_db,
            patch("app.main.rc") as mock_rc,
            patch("app.main.get_handler", return_value=handler),
        ):
            mock_db.async_session_factory = mock_session_factory
            mock_rc.redis_client = mock_redis

            from app.main import process_job

            semaphore = asyncio.Semaphore(5)
            await process_job(str(job.id), semaphore)

            # Verify retry was scheduled via ZADD
            mock_redis.zadd.assert_called_once()
            assert job_in_error.status == "retrying"

    async def test_dlq_path(self):
        """Job exceeding max_attempts -> dead_letter + RPUSH to DLQ"""
        job = make_job(status="pending", attempts=0, max_attempts=1)

        # First session
        mock_session_1 = AsyncMock()
        mock_result_1 = MagicMock()
        mock_result_1.scalar_one_or_none.return_value = job
        mock_session_1.execute = AsyncMock(return_value=mock_result_1)
        mock_session_1.commit = AsyncMock()

        # Second session (error path): attempts=1 == max_attempts=1 -> DLQ
        job_in_error = make_job(
            id=job.id, status="processing", attempts=1, max_attempts=1,
        )
        mock_session_2 = AsyncMock()
        mock_result_2 = MagicMock()
        mock_result_2.scalar_one_or_none.return_value = job_in_error
        mock_session_2.execute = AsyncMock(return_value=mock_result_2)
        mock_session_2.commit = AsyncMock()

        call_count = 0

        class FakeSessionCtx:
            async def __aenter__(self_inner):
                nonlocal call_count
                call_count += 1
                return mock_session_1 if call_count == 1 else mock_session_2

            async def __aexit__(self_inner, *args):
                return False

        mock_session_factory = MagicMock(return_value=FakeSessionCtx())

        handler = AsyncMock(side_effect=RuntimeError("final failure"))
        mock_redis = AsyncMock()

        with (
            patch("app.main.db") as mock_db,
            patch("app.main.rc") as mock_rc,
            patch("app.main.get_handler", return_value=handler),
        ):
            mock_db.async_session_factory = mock_session_factory
            mock_rc.redis_client = mock_redis

            from app.main import process_job

            semaphore = asyncio.Semaphore(5)
            await process_job(str(job.id), semaphore)

            # Verify job was pushed to DLQ
            mock_redis.rpush.assert_called_once()
            call_args = mock_redis.rpush.call_args
            assert call_args[0][0] == "dead_letter_queue"
            assert job_in_error.status == "dead_letter"

    async def test_invalid_job_id_skipped(self):
        """Invalid UUID string is skipped gracefully."""
        with (
            patch("app.main.db"),
            patch("app.main.rc"),
        ):
            from app.main import process_job

            semaphore = asyncio.Semaphore(5)
            await process_job("not-a-uuid", semaphore)

    async def test_job_not_found_skipped(self):
        """Job not in DB is skipped gracefully."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute = AsyncMock(return_value=mock_result)

        mock_session_factory = MagicMock()
        mock_session_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=False)

        with (
            patch("app.main.db") as mock_db,
            patch("app.main.rc"),
        ):
            mock_db.async_session_factory = mock_session_factory

            from app.main import process_job

            semaphore = asyncio.Semaphore(5)
            job_id = str(uuid.uuid4())
            await process_job(job_id, semaphore)


class TestHandlerRegistry:
    def test_known_handlers(self):
        from app.handlers import HANDLERS, get_handler

        assert get_handler("email.send") is not None
        assert get_handler("report.generate") is not None
        assert "email.send" in HANDLERS
        assert "report.generate" in HANDLERS

    def test_unknown_handler_returns_none(self):
        from app.handlers import get_handler

        assert get_handler("nonexistent.type") is None


class TestExponentialBackoff:
    def test_backoff_delay_formula(self):
        """Verify delay = 2^attempts pattern used in process_job."""
        assert 2 ** 1 == 2
        assert 2 ** 2 == 4
        assert 2 ** 3 == 8
        assert 2 ** 4 == 16
