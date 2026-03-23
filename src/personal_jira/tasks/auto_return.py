import asyncio
import logging

from personal_jira.database import get_async_session
from personal_jira.services.auto_return import (
    AUTO_RETURN_TIMEOUT_MINUTES,
    AutoReturnService,
)

logger = logging.getLogger(__name__)

AUTO_RETURN_INTERVAL_SECONDS: int = 60

_service = AutoReturnService()


async def run_auto_return_cycle() -> None:
    async with get_async_session() as db:
        returned = await _service.return_stale_issues(db)
        if returned:
            logger.info("Auto-return cycle: returned %d issues", len(returned))


async def auto_return_background_loop() -> None:
    logger.info(
        "Starting auto-return background task (timeout=%dm, interval=%ds)",
        AUTO_RETURN_TIMEOUT_MINUTES,
        AUTO_RETURN_INTERVAL_SECONDS,
    )
    while True:
        try:
            await run_auto_return_cycle()
        except Exception:
            logger.exception("Error in auto-return background task")
        await asyncio.sleep(AUTO_RETURN_INTERVAL_SECONDS)
