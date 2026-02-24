from typing import Awaitable, Callable

from app.handlers.email_send import handle_email_send
from app.handlers.report_generate import handle_report_generate

JobHandler = Callable[[dict], Awaitable[dict | None]]

HANDLERS: dict[str, JobHandler] = {
    "report.generate": handle_report_generate,
    "email.send": handle_email_send,
}


def get_handler(job_type: str) -> JobHandler | None:
    """Look up a handler for the given job type. Returns None if unknown."""
    return HANDLERS.get(job_type)
