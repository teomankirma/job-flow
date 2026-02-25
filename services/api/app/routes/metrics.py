from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models import Job
from app.redis_client import get_redis

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def get_metrics(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    result = await session.execute(
        select(
            func.count().label("total_jobs"),
            func.count().filter(Job.status == "processing").label("active_jobs"),
            func.count().filter(Job.status == "completed").label("completed_jobs"),
            func.count().filter(Job.status == "failed").label("failed_jobs"),
            func.count().filter(Job.status == "dead_letter").label("dead_letter_jobs"),
        ).select_from(Job)
    )
    row = result.one()

    queue_length = await redis.llen("job_queue")
    retry_queue_length = await redis.zcard("retry_queue")
    dlq_length = await redis.llen("dead_letter_queue")

    return {
        "total_jobs": row.total_jobs,
        "active_jobs": row.active_jobs,
        "completed_jobs": row.completed_jobs,
        "failed_jobs": row.failed_jobs,
        "dead_letter_jobs": row.dead_letter_jobs,
        "queue_length": queue_length,
        "retry_queue_length": retry_queue_length,
        "dlq_length": dlq_length,
    }
