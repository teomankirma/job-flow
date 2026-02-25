import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.database import get_session
from app.main import app
from tests.conftest import make_job, mock_session_with_result, override_session


@pytest.mark.asyncio
class TestCreateJob:
    async def test_invalid_type_returns_422(self, client):
        response = await client.post("/jobs", json={
            "type": "invalid.type",
            "payload": {},
        })
        assert response.status_code == 422

    async def test_missing_payload_returns_422(self, client):
        response = await client.post("/jobs", json={
            "type": "email.send",
        })
        assert response.status_code == 422

    async def test_create_job_success(self, client, fake_redis):
        def populate_job_fields(job):
            """Simulate DB populating server-default fields after refresh."""
            from datetime import datetime, timezone
            job.id = uuid.uuid4()
            job.status = job.status or "pending"
            job.attempts = job.attempts if job.attempts is not None else 0
            now = datetime.now(timezone.utc).replace(tzinfo=None)
            job.created_at = now
            job.updated_at = now

        mock_session = AsyncMock()
        mock_session.add = MagicMock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock(side_effect=populate_job_fields)

        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.post("/jobs", json={
            "type": "email.send",
            "payload": {"to": "user@example.com"},
        })
        assert response.status_code == 201
        data = response.json()
        assert data["type"] == "email.send"
        assert data["status"] == "pending"
        mock_session.add.assert_called_once()

    async def test_idempotency_key_returns_existing(self, client, fake_redis):
        job = make_job(idempotency_key="test-key-1")

        mock_session = mock_session_with_result(job)
        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.post(
            "/jobs",
            json={"type": "email.send", "payload": {}},
            headers={"Idempotency-Key": "test-key-1"},
        )
        assert response.status_code == 200
        assert response.json()["id"] == str(job.id)


@pytest.mark.asyncio
class TestGetJob:
    async def test_found(self, client):
        job = make_job()

        mock_session = mock_session_with_result(job)
        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.get(f"/jobs/{job.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(job.id)
        assert data["status"] == "pending"

    async def test_not_found(self, client):
        mock_session = mock_session_with_result(None)
        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.get(f"/jobs/{uuid.uuid4()}")
        assert response.status_code == 404


@pytest.mark.asyncio
class TestListJobs:
    async def test_empty_list(self, client):
        mock_session = AsyncMock()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.get("/jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_status_filter_accepted(self, client):
        mock_session = AsyncMock()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 0

        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = []

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.get("/jobs?status=completed")
        assert response.status_code == 200

    async def test_with_items(self, client):
        jobs = [make_job() for _ in range(3)]

        mock_session = AsyncMock()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 3

        items_result = MagicMock()
        items_result.scalars.return_value.all.return_value = jobs

        mock_session.execute = AsyncMock(side_effect=[count_result, items_result])

        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.get("/jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3


@pytest.mark.asyncio
class TestRetryJob:
    async def test_retry_failed_job(self, client, fake_redis):
        job = make_job(status="failed", attempts=1, error_message="some error")

        mock_session = mock_session_with_result(job)
        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.post(f"/jobs/{job.id}/retry")
        assert response.status_code == 200
        assert response.json()["status"] == "pending"

    async def test_retry_dead_letter_job(self, client, fake_redis):
        job = make_job(status="dead_letter", attempts=3, error_message="max retries")

        mock_session = mock_session_with_result(job)
        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.post(f"/jobs/{job.id}/retry")
        assert response.status_code == 200

    async def test_retry_completed_job_returns_409(self, client):
        job = make_job(status="completed")

        mock_session = mock_session_with_result(job)
        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.post(f"/jobs/{job.id}/retry")
        assert response.status_code == 409

    async def test_retry_not_found(self, client):
        mock_session = mock_session_with_result(None)
        app.dependency_overrides[get_session] = override_session(mock_session)

        response = await client.post(f"/jobs/{uuid.uuid4()}/retry")
        assert response.status_code == 404
