"""
Logging configuration for TLC4Pipe backend.
Provides JSON-formatted logs with request correlation and optional file rotation.
"""

import json
import logging
import logging.config
import os
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, Optional

# Context variable to store the current request id
request_id_ctx: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """Return the current request id if set."""
    return request_id_ctx.get()


def set_request_id(value: Optional[str]) -> None:
    """Set the current request id in the context."""
    request_id_ctx.set(value)


class RequestIdFilter(logging.Filter):
    """Inject request_id from contextvars into log records."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        record.request_id = get_request_id() or "-"
        return True


class JsonFormatter(logging.Formatter):
    """Render log records as JSON strings."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: D401
        log_record: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Optional context
        if hasattr(record, "request_id"):
            log_record["request_id"] = getattr(record, "request_id")
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record["stack_info"] = self.formatStack(record.stack_info)

        return json.dumps(log_record, ensure_ascii=True)


def build_logging_config(level: str = "INFO", log_file: Optional[str] = None, enable_sql: bool = False) -> Dict[str, Any]:
    """Return dictConfig compatible logging configuration."""
    handlers: Dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "json",
            "filters": ["request_id"],
            "stream": "ext://sys.stdout",
        }
    }

    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": level,
            "formatter": "json",
            "filters": ["request_id"],
            "filename": log_file,
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 3,
            "encoding": "utf-8",
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "request_id": {
                "()": RequestIdFilter,
            },
        },
        "formatters": {
            "json": {
                "()": JsonFormatter,
            }
        },
        "handlers": handlers,
        "root": {
            "level": level,
            "handlers": list(handlers.keys()),
        },
        "loggers": {
            "uvicorn": {"level": level, "handlers": list(handlers.keys()), "propagate": False},
            "uvicorn.error": {"level": level, "handlers": list(handlers.keys()), "propagate": False},
            "uvicorn.access": {"level": level, "handlers": list(handlers.keys()), "propagate": False},
            "sqlalchemy.engine": {"level": "INFO" if enable_sql else "WARNING", "handlers": list(handlers.keys()), "propagate": False},
        },
    }


def setup_logging(level: str = "INFO", log_file: Optional[str] = None, enable_sql: bool = False) -> None:
    """Apply logging configuration using dictConfig."""
    config = build_logging_config(level=level, log_file=log_file, enable_sql=enable_sql)
    logging.config.dictConfig(config)