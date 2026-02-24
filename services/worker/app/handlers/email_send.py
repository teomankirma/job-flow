import asyncio
import logging

logger = logging.getLogger(__name__)


async def handle_email_send(payload: dict) -> dict:
    """Simulate sending an email. Always succeeds."""
    to = payload.get("to", "unknown@example.com")
    subject = payload.get("subject", "(no subject)")

    logger.info("Sending email to '%s' with subject '%s'", to, subject)
    await asyncio.sleep(1.0)
    logger.info("Email sent successfully to '%s'", to)

    return {"to": to, "subject": subject, "delivered": True}
