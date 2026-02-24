import asyncio
import logging
import os
import signal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

shutdown_event = asyncio.Event()


def handle_signal(sig, _frame):
    logger.info("Received signal %s, shutting down...", sig)
    shutdown_event.set()


async def main():
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)

    logger.info("Worker starting...")
    logger.info("REDIS_URL: %s", os.getenv("REDIS_URL", "not set"))
    logger.info("DATABASE_URL: %s", "set" if os.getenv("DATABASE_URL") else "not set")

    while not shutdown_event.is_set():
        logger.info("Worker heartbeat - waiting for jobs...")
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=5.0)
        except asyncio.TimeoutError:
            continue

    logger.info("Worker shut down gracefully.")


if __name__ == "__main__":
    asyncio.run(main())
