from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from pytz import utc

from tgbot.config import settings
from .jobs import send_daily_stats, send_weekly_stats, remind_couriers


async def setup_scheduler(bot, pool) -> AsyncIOScheduler:
    """Настройка планировщика задач"""
    
    # Настройки планировщика
    jobstores = {
        'default': MemoryJobStore()
    }
    
    executors = {
        'default': AsyncIOExecutor()
    }
    
    job_defaults = {
        'coalesce': False,
        'max_instances': 3,
        'misfire_grace_time': 3600
    }
    
    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=settings.scheduler.timezone
    )
    
    # Ежедневная статистика в 23:00
    scheduler.add_job(
        send_daily_stats,
        'cron',
        args=[bot, pool],
        hour=23,
        minute=0,
        id='daily_stats',
        replace_existing=True
    )
    
    # Еженедельная статистика в воскресенье в 23:30
    scheduler.add_job(
        send_weekly_stats,
        'cron',
        args=[bot, pool],
        day_of_week='sun',
        hour=23,
        minute=30,
        id='weekly_stats',
        replace_existing=True
    )
    
    # Напоминание курьерам каждые 3 часа
    scheduler.add_job(
        remind_couriers,
        'interval',
        args=[bot, pool],
        hours=3,
        id='courier_reminder',
        replace_existing=True
    )
    
    return scheduler