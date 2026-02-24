import asyncio
import logging
import random

logger = logging.getLogger(__name__)


async def handle_report_generate(payload: dict) -> dict:
    """Simulate report generation. Sleeps 2-5s, fails ~30% of the time."""
    report_name = payload.get("name", "unnamed-report")

    duration = random.uniform(2.0, 5.0)
    logger.info("Generating report '%s', estimated duration: %.1fs", report_name, duration)
    await asyncio.sleep(duration)

    if random.random() < 0.3:
        raise RuntimeError(f"Report generation failed for '{report_name}': simulated transient error")

    return {"report_name": report_name, "pages": random.randint(1, 50)}
