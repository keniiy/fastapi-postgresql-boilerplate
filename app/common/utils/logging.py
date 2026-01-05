"""
Structured logging configuration with trace ID support.
"""
import logging
import sys
from contextvars import ContextVar
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger

# Context variable for trace ID (accessible globally)
trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def get_trace_id() -> Optional[str]:
    """Get current trace ID from context"""
    return trace_id_var.get()


def set_trace_id(trace_id: Optional[str]) -> None:
    """Set trace ID in context"""
    trace_id_var.set(trace_id)


class TraceIDFilter(logging.Filter):
    """Logging filter to add trace ID to log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add trace ID to log record"""
        record.trace_id = get_trace_id() or "N/A"
        return True


def setup_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    """
    Configure application logging with structured JSON format and trace ID support.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON format (True) or standard format (False)
    """
    # Convert string level to logging constant
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Add trace ID filter
    handler.addFilter(TraceIDFilter())

    # Configure formatter
    if json_format:
        # JSON structured logging (for production/log aggregation)
        class JsonFormatterWithTraceID(jsonlogger.JsonFormatter):
            """JSON formatter with trace ID support"""

            def format(self, record):
                # Add trace_id to record before formatting
                if not hasattr(record, "trace_id"):
                    record.trace_id = get_trace_id() or "N/A"
                return super().format(record)

        formatter = JsonFormatterWithTraceID(
            fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(trace_id)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            rename_fields={
                "asctime": "timestamp",
                "name": "logger",
                "levelname": "level",
                "message": "message",
                "trace_id": "trace_id",
            },
            static_fields={"service": "api"},
        )
    else:
        # Standard readable format (for development)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | [%(trace_id)s] | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Set levels for noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for the given name.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
