"""
Base task class with common functionality.
"""

import logging
from typing import Any

from celery import Task

from app.common.utils.logging import set_trace_id

logger = logging.getLogger(__name__)


class BaseTask(Task):
    """
    Base task class with:
    - Automatic trace ID propagation
    - Error logging
    - Retry logic
    """

    # Default retry settings
    autoretry_for = (Exception,)
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True
    max_retries = 3

    def before_start(
        self,
        task_id: str,
        args: tuple,
        kwargs: dict,
    ) -> None:
        """Called before task starts"""
        # Set trace ID from kwargs if provided
        trace_id = kwargs.pop("_trace_id", None) or task_id
        set_trace_id(trace_id)

        logger.info(
            f"Task started: {self.name}", extra={"task_id": task_id, "args": args, "kwargs": kwargs}
        )

    def on_success(
        self,
        retval: Any,
        task_id: str,
        args: tuple,
        kwargs: dict,
    ) -> None:
        """Called on task success"""
        logger.info(
            f"Task completed: {self.name}", extra={"task_id": task_id, "result": str(retval)[:100]}
        )

    def on_failure(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,
        kwargs: dict,
        einfo: Any,
    ) -> None:
        """Called on task failure"""
        logger.error(
            f"Task failed: {self.name}",
            extra={
                "task_id": task_id,
                "error": str(exc),
                "args": args,
                "kwargs": kwargs,
            },
            exc_info=True,
        )

    def on_retry(
        self,
        exc: Exception,
        task_id: str,
        args: tuple,
        kwargs: dict,
        einfo: Any,
    ) -> None:
        """Called on task retry"""
        logger.warning(
            f"Task retrying: {self.name}",
            extra={
                "task_id": task_id,
                "error": str(exc),
                "retry_count": self.request.retries,
            },
        )

    def after_return(
        self,
        status: str,
        retval: Any,
        task_id: str,
        args: tuple,
        kwargs: dict,
        einfo: Any,
    ) -> None:
        """Called after task returns (success or failure)"""
        # Clear trace ID
        set_trace_id(None)
