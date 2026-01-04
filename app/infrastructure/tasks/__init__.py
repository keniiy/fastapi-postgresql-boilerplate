"""
Celery task infrastructure for background job processing.
"""
from app.infrastructure.tasks.celery_app import celery_app
from app.infrastructure.tasks.base import BaseTask

__all__ = [
    "celery_app",
    "BaseTask",
]
