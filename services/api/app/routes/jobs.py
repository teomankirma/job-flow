import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Job
from app.redis_client import get_redis
from app.schemas import JobCreateRequest, JobListResponse, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", status_code=201, response_model=JobResponse)
async def create_job(
    body: JobCreateRequest,
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    job = Job(
        type=body.type.value,
        payload=body.payload,
        max_attempts=body.max_attempts,
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    await redis.rpush("job_queue", str(job.id))

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
    session: AsyncSession = Depends(get_session),
):
    count_result = await session.execute(select(func.count()).select_from(Job))
    total = count_result.scalar_one()

    result = await session.execute(
        select(Job).order_by(Job.created_at.desc()).limit(limit).offset(offset)
    )
    items = result.scalars().all()

    return JobListResponse(items=items, total=total, limit=limit, offset=offset)
