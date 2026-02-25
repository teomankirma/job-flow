import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.models import Job


def make_job(**kwargs) -> MagicMock:
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
    job = MagicMock(spec=Job)
    for k, v in defaults.items():
        setattr(job, k, v)
    return job
