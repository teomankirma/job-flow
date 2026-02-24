import os


class Config:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    REDIS_URL: str = os.environ["REDIS_URL"]

    # Queue name — must match API's rpush target in routes/jobs.py
    QUEUE_NAME: str = os.getenv("QUEUE_NAME", "job_queue")

    # Max concurrent jobs per worker instance
    MAX_CONCURRENCY: int = int(os.getenv("MAX_CONCURRENCY", "5"))

    # BLPOP timeout in seconds (controls shutdown responsiveness)
    QUEUE_POLL_TIMEOUT: int = int(os.getenv("QUEUE_POLL_TIMEOUT", "1"))
