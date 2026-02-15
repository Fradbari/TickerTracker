import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from datetime import datetime
import pytz
import time

logger = logging.getLogger("scheduler")

# UTC timezone
UTC = pytz.UTC

# Job metrics
job_metrics = {}

def log_job_start(job_name):
    logger.info(f"[JOB START] {job_name} at {datetime.utcnow().isoformat()}Z")
    job_metrics[job_name] = {"start": time.monotonic()}

def log_job_end(job_name, success=True):
    duration = time.monotonic() - job_metrics[job_name]["start"]
    logger.info(f"[JOB END] {job_name} duration={duration:.2f}s success={success}")
    job_metrics[job_name]["duration"] = duration
    job_metrics[job_name]["success"] = success

def job_wrapper(job_func, job_name):
    async def wrapped(*args, **kwargs):
        log_job_start(job_name)
        try:
            await job_func(*args, **kwargs)
            log_job_end(job_name, success=True)
        except Exception as e:
            logger.exception(f"[JOB ERROR] {job_name}: {e}")
            log_job_end(job_name, success=False)
    return wrapped

# Example job implementations (replace with real logic)
async def refresh_market_data():
    # ... fetch and update market data ...
    pass

async def daily_history_sync():
    # ... sync daily history ...
    pass

async def refresh_materialized_views():
    # ... refresh materialized views ...
    pass

async def check_targets():
    # ... check for target/stop hits ...
    pass

def create_scheduler():
    scheduler = AsyncIOScheduler(
        jobstores={"default": MemoryJobStore()},
        executors={"default": AsyncIOExecutor()},
        timezone=UTC
    )
    # Job: refresh_market_data (ogni 5 minuti, orari di mercato)
    scheduler.add_job(
        job_wrapper(refresh_market_data, "refresh_market_data"),
        CronTrigger(minute="*/5", hour="14-21", day_of_week="mon-fri", timezone=UTC),
        id="refresh_market_data",
        replace_existing=True
    )
    # Job: daily_history_sync (ogni giorno alle 23:00 UTC)
    scheduler.add_job(
        job_wrapper(daily_history_sync, "daily_history_sync"),
        CronTrigger(hour=23, minute=0, timezone=UTC),
        id="daily_history_sync",
        replace_existing=True
    )
    # Job: refresh_materialized_views (ogni 5 minuti)
    scheduler.add_job(
        job_wrapper(refresh_materialized_views, "refresh_materialized_views"),
        CronTrigger(minute="*/5", timezone=UTC),
        id="refresh_materialized_views",
        replace_existing=True
    )
    # Job: check_targets (ogni minuto)
    scheduler.add_job(
        job_wrapper(check_targets, "check_targets"),
        IntervalTrigger(minutes=1),
        id="check_targets",
        replace_existing=True
    )
    return scheduler

# FastAPI integration
scheduler = None

def start_scheduler():
    global scheduler
    if scheduler is None:
        scheduler = create_scheduler()
        scheduler.start()
        logger.info("APScheduler started.")

def shutdown_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=True)
        logger.info("APScheduler shutdown.")
        scheduler = None
