import asyncio
import logging
import signal
import time
import uuid
from datetime import datetime, timezone


def _utcnow() -> datetime:
    """Return a naive UTC datetime (matches TIMESTAMP WITHOUT TIME ZONE columns)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

from sqlalchemy import select

from app.config import Config
from app import database as db
from app.handlers import get_handler
from app.log_config import setup_logging
from app.models import Job
from app import redis_client as rc

logger = logging.getLogger(__name__)

shutdown_event = asyncio.Event()
in_flight_tasks: set[asyncio.Task] = set()

# Lua script: atomically move due jobs from retry ZSET to main queue.
# Prevents double-queuing even with multiple worker instances.
PROMOTE_RETRY_SCRIPT = """
local members = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ARGV[1], 'LIMIT', 0, 10)
for _, member in ipairs(members) do
    redis.call('ZREM', KEYS[1], member)
    redis.call('RPUSH', KEYS[2], member)
end
return #members
"""


def handle_signal(sig: int, _frame) -> None:
    logger.info(
        "Received signal %s, initiating graceful shutdown...",
        signal.Signals(sig).name,
    )
    shutdown_event.set()


async def process_job(job_id_str: str, semaphore: asyncio.Semaphore) -> None:
    async with semaphore:
        start_time = time.monotonic()

        try:
            job_id = uuid.UUID(job_id_str)
        except ValueError:
            logger.error("Invalid job ID from queue: '%s', skipping", job_id_str)
            return

        log_extra: dict = {"job_id": str(job_id)}

        try:
            async with db.async_session_factory() as session:
                result = await session.execute(select(Job).where(Job.id == job_id))
                job = result.scalar_one_or_none()

                if job is None:
                    logger.warning("Job not found in database, skipping", extra=log_extra)
                    return

                log_extra["job_type"] = job.type

                if job.status not in ("pending", "retrying"):
                    logger.warning(
                        "Job status is '%s', expected 'pending' or 'retrying', skipping",
                        job.status,
                        extra=log_extra,
                    )
                    return

                # Transition to processing
                job.status = "processing"
                job.attempts += 1
                job.updated_at = _utcnow()
                await session.commit()

                log_extra["attempts"] = job.attempts
                logger.info("Job started", extra=log_extra)

                # Look up and execute handler
                handler = get_handler(job.type)
                if handler is None:
                    raise ValueError(f"Unknown job type: '{job.type}'")

                await handler(job.payload)

                # Success
                job.status = "completed"
                job.error_message = None
                job.updated_at = _utcnow()
                await session.commit()

                duration_ms = int((time.monotonic() - start_time) * 1000)
                logger.info(
                    "Job completed",
                    extra={**log_extra, "status": "completed", "duration_ms": duration_ms},
                )

        except Exception as exc:
            duration_ms = int((time.monotonic() - start_time) * 1000)
            error_msg = f"{type(exc).__name__}: {exc}"

            logger.error(
                "Job failed: %s",
                error_msg,
                extra={**log_extra, "status": "failed", "error": error_msg, "duration_ms": duration_ms},
            )

            try:
                async with db.async_session_factory() as session:
                    result = await session.execute(select(Job).where(Job.id == job_id))
                    job = result.scalar_one_or_none()
                    if job:
                        if job.attempts < job.max_attempts:
                            # Schedule retry with exponential backoff
                            delay = 2 ** job.attempts
                            retry_at = time.time() + delay
                            job.status = "retrying"
                            job.error_message = error_msg[:2000]
                            job.updated_at = _utcnow()
                            await session.commit()

                            await rc.redis_client.zadd(
                                Config.RETRY_QUEUE_NAME, {str(job_id): retry_at}
                            )

                            logger.info(
                                "Job scheduled for retry in %ds (attempt %d/%d)",
                                delay,
                                job.attempts,
                                job.max_attempts,
                                extra={
                                    **log_extra,
                                    "status": "retrying",
                                    "retry_delay_s": delay,
                                },
                            )
                        else:
                            # Max attempts exceeded -> dead-letter queue
                            job.status = "dead_letter"
                            job.error_message = error_msg[:2000]
                            job.updated_at = _utcnow()
                            await session.commit()

                            await rc.redis_client.rpush(
                                Config.DLQ_NAME, str(job_id)
                            )

                            logger.warning(
                                "Job moved to dead-letter queue after %d attempts",
                                job.attempts,
                                extra={**log_extra, "status": "dead_letter"},
                            )
            except Exception as db_exc:
                logger.error(
                    "Failed to update job status in DB: %s",
                    db_exc,
                    extra=log_extra,
                )


async def retry_scheduler() -> None:
    """Periodically move due jobs from retry ZSET to main queue."""
    logger.info(
        "Retry scheduler started (poll_interval=%.1fs)",
        Config.RETRY_POLL_INTERVAL,
    )

    promote_script = rc.redis_client.register_script(PROMOTE_RETRY_SCRIPT)

    while not shutdown_event.is_set():
        try:
            now = time.time()
            promoted = await promote_script(
                keys=[Config.RETRY_QUEUE_NAME, Config.QUEUE_NAME],
                args=[now],
            )
            if promoted and promoted > 0:
                logger.info("Promoted %d job(s) from retry queue", promoted)
        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.error("Error in retry scheduler: %s", exc, exc_info=True)

        await asyncio.sleep(Config.RETRY_POLL_INTERVAL)

    logger.info("Retry scheduler stopped")


async def worker_loop() -> None:
    semaphore = asyncio.Semaphore(Config.MAX_CONCURRENCY)
    queue_name = Config.QUEUE_NAME
    poll_timeout = Config.QUEUE_POLL_TIMEOUT

    logger.info(
        "Worker loop started (queue=%s, concurrency=%d, poll_timeout=%ds)",
        queue_name,
        Config.MAX_CONCURRENCY,
        poll_timeout,
    )

    while not shutdown_event.is_set():
        try:
            job_id_str = await rc.redis_client.lpop(queue_name)

            if job_id_str is None:
                await asyncio.sleep(poll_timeout)
                continue

            logger.info("Job received from queue", extra={"job_id": job_id_str})

            task = asyncio.create_task(process_job(job_id_str, semaphore))
            in_flight_tasks.add(task)
            task.add_done_callback(in_flight_tasks.discard)

        except asyncio.CancelledError:
            break
        except Exception as exc:
            logger.error("Error in worker loop: %s", exc, exc_info=True)
            await asyncio.sleep(1.0)

    if in_flight_tasks:
        logger.info("Waiting for %d in-flight job(s) to complete...", len(in_flight_tasks))
        await asyncio.gather(*in_flight_tasks, return_exceptions=True)

    logger.info("Worker loop stopped")


async def main() -> None:
    setup_logging()

    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    logger.info("Worker starting...")

    db.init_db()
    rc.init_redis()

    logger.info("Connected to database and Redis")

    try:
        await asyncio.gather(
            worker_loop(),
            retry_scheduler(),
        )
    finally:
        await rc.close_redis()
        await db.close_db()
        logger.info("Worker shut down gracefully")


if __name__ == "__main__":
    asyncio.run(main())
