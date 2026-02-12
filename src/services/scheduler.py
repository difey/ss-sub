from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.routers.subscription import refresh_subscriptions
import logging

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def scheduled_refresh():
    logger.info("Starting scheduled subscription refresh...")
    try:
        await refresh_subscriptions()
        logger.info("Scheduled subscription refresh completed.")
    except Exception as e:
        logger.error(f"Scheduled subscription refresh failed: {e}")

def start_scheduler():
    scheduler.add_job(
        scheduled_refresh,
        trigger=IntervalTrigger(minutes=10),
        id="refresh_subscriptions",
        name="Refresh Subscriptions",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started.")

def stop_scheduler():
    scheduler.shutdown()
    logger.info("Scheduler stopped.")
