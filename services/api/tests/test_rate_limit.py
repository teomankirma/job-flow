import uuid
from unittest.mock import patch

import pytest

from app.database import get_session
from app.main import app
from tests.conftest import FakeRedis, mock_session_with_result, override_session


@pytest.mark.asyncio
class TestRateLimiting:
    async def test_get_requests_bypass_rate_limit(self, client):
        mock_session = mock_session_with_result(None)
        app.dependency_overrides[get_session] = override_session(mock_session)

        # GET requests should never get 429, even with many requests
        for _ in range(10):
            response = await client.get(f"/jobs/{uuid.uuid4()}")
            assert response.status_code == 404  # not 429

    async def test_post_rate_limited_after_threshold(self, client):
        fake = FakeRedis()

        with patch("app.middleware.rate_limit.redis_client", fake):
            # Send POST requests with invalid body -> gets 422 from validation
            # but still counted by rate limiter
            responses = []
            for _ in range(65):
                response = await client.post("/jobs", json={
                    "type": "bad.type",
                    "payload": {},
                })
                responses.append(response.status_code)

            # First 60 requests pass rate limiter (return 422 from validation)
            # Requests 61+ should get 429 from rate limiter
            has_429 = 429 in responses
            assert has_429, f"Expected 429 in responses, got: {set(responses)}"

    async def test_429_includes_retry_after_header(self, client):
        fake = FakeRedis()

        with patch("app.middleware.rate_limit.redis_client", fake):
            # Burn through the rate limit
            for _ in range(61):
                await client.post("/jobs", json={
                    "type": "bad.type",
                    "payload": {},
                })

            # Next request should be 429 with Retry-After
            response = await client.post("/jobs", json={
                "type": "bad.type",
                "payload": {},
            })
            assert response.status_code == 429
            assert "retry-after" in response.headers
