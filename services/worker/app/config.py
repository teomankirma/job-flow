import os


class Config:
    DATABASE_URL: str = os.environ["DATABASE_URL"]
    REDIS_URL: str = os.environ["REDIS_URL"]

    # Queue name — must match API's rpush target in routes/jobs.py
    QUEUE_NAME: str = os.getenv("QUEUE_NAME", "job_queue")

    # Retry queue (Redis sorted set, scored by retry-at timestamp)
    RETRY_QUEUE_NAME: str = os.getenv("RETRY_QUEUE_NAME", "retry_queue")

    # Dead-letter queue (Redis list for jobs exceeding max_attempts)
    DLQ_NAME: str = os.getenv("DLQ_NAME", "dead_letter_queue")

    # Max concurrent jobs per worker instance
    MAX_CONCURRENCY: int = int(os.getenv("MAX_CONCURRENCY", "5"))

    # BLPOP timeout in seconds (controls shutdown responsiveness)
    QUEUE_POLL_TIMEOUT: int = int(os.getenv("QUEUE_POLL_TIMEOUT", "1"))

    # How often the retry scheduler checks for due jobs (seconds)
    RETRY_POLL_INTERVAL: float = float(os.getenv("RETRY_POLL_INTERVAL", "1.0"))
