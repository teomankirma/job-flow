import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class JobType(str, Enum):
    email_send = "email.send"
    report_generate = "report.generate"
    image_process = "image.process"


class JobCreateRequest(BaseModel):
    type: JobType
    payload: dict
    max_attempts: int = Field(default=3, ge=1)


class JobResponse(BaseModel):
    id: uuid.UUID
    type: str
    payload: dict
    status: JobStatus
    attempts: int
    max_attempts: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int
    limit: int
    offset: int
