"""
Celery application configuration.
"""

from celery import Celery

from app.core.config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "app",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "app.infrastructure.tasks.email_tasks",
        "app.infrastructure.tasks.user_tasks",
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution settings
    task_acks_late=True,  # Acknowledge task after completion
    task_reject_on_worker_lost=True,  # Reject task if worker dies
    worker_prefetch_multiplier=1,  # Fetch one task at a time
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    # Task routing (optional - for scaling)
    task_routes={
        "app.infrastructure.tasks.email_tasks.*": {"queue": "email"},
        "app.infrastructure.tasks.user_tasks.*": {"queue": "default"},
    },
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    # Beat scheduler (for periodic tasks)
    beat_schedule={
        "cleanup-expired-tokens": {
            "task": "app.infrastructure.tasks.user_tasks.cleanup_expired_tokens",
            "schedule": 3600.0,  # Every hour
        },
    },
)


# Task base class with common settings
class TaskConfig:
    """Default task configuration"""

    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes max backoff
    retry_jitter = True
