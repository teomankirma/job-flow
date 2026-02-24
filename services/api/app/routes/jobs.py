import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Job
from app.redis_client import get_redis
from app.schemas import JobCreateRequest, JobListResponse, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse)
async def create_job(
    body: JobCreateRequest,
    response: Response,
    idempotency_key: str | None = Header(None, alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    # If idempotency key provided, check for existing job
    if idempotency_key is not None:
        result = await session.execute(
            select(Job).where(Job.idempotency_key == idempotency_key)
        )
        existing_job = result.scalar_one_or_none()
        if existing_job is not None:
            response.status_code = 200
            return existing_job

    job = Job(
        type=body.type.value,
        payload=body.payload,
        max_attempts=body.max_attempts,
        idempotency_key=idempotency_key,
    )
    session.add(job)

    try:
        await session.commit()
    except IntegrityError:
        # Race condition: another request with the same key committed first
        await session.rollback()
        result = await session.execute(
            select(Job).where(Job.idempotency_key == idempotency_key)
        )
        existing_job = result.scalar_one()
        response.status_code = 200
        return existing_job

    await session.refresh(job)
    await redis.rpush("job_queue", str(job.id))

    response.status_code = 201
    return job


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("", response_model=JobListResponse)
async def list_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    status: str | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    base_query = select(Job)
    count_query = select(func.count()).select_from(Job)

    if status is not None:
        base_query = base_query.where(Job.status == status)
        count_query = count_query.where(Job.status == status)

    count_result = await session.execute(count_query)
    total = count_result.scalar_one()

    result = await session.execute(
        base_query.order_by(Job.created_at.desc()).limit(limit).offset(offset)
    )
    items = result.scalars().all()

    return JobListResponse(items=items, total=total, limit=limit, offset=offset)
