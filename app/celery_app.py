from celery import Celery
from app.config import settings

celery_app = Celery(
    "kad_monitor",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks"],
)
celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "dispatch-kad-checks-every-minute": {
            "task": "app.tasks.dispatch_checks",
            "schedule": 60.0,
        }
    },
)
