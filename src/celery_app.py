from celery import Celery
from celery.schedules import crontab
from .config import settings

# Create Celery instance
celery_app = Celery(
    "task_manager",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.tasks.celery_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # 1 hour
    task_routes={
        "src.tasks.celery_tasks.*": {"queue": "tasks"},
    },
    beat_schedule={
        # Example: Check for overdue tasks every hour
        "check-overdue-tasks": {
            "task": "src.tasks.celery_tasks.check_overdue_tasks",
            "schedule": crontab(minute=0),  # Every hour at minute 0
        },
        # Example: Daily cleanup
        "daily-cleanup": {
            "task": "src.tasks.celery_tasks.daily_cleanup",
            "schedule": crontab(hour=2, minute=0),  # Every day at 2:00 AM
        },
    },
)

# Optional: Configure worker
celery_app.conf.worker_prefetch_multiplier = 1
celery_app.conf.task_acks_late = True 