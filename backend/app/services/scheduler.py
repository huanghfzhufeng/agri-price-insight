from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.ingestion import run_moa_daily_ingestion, run_moa_monthly_report_sync


settings = get_settings()


def start_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)

    def run_daily_sync() -> None:
        with SessionLocal() as db:
            run_moa_daily_ingestion(db, pages=3, max_articles=20)

    def run_monthly_sync() -> None:
        with SessionLocal() as db:
            run_moa_monthly_report_sync(db, limit=12)

    scheduler.add_job(
        run_daily_sync,
        trigger="cron",
        id="moa_daily_sync",
        replace_existing=True,
        hour=settings.daily_sync_hour,
        minute=settings.daily_sync_minute,
    )
    scheduler.add_job(
        run_monthly_sync,
        trigger="cron",
        id="moa_monthly_sync",
        replace_existing=True,
        day=settings.monthly_sync_day,
        hour=settings.monthly_sync_hour,
        minute=settings.monthly_sync_minute,
    )
    scheduler.start()
    return scheduler
