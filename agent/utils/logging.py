import logging
import json
from datetime import datetime
from logging import Logger


class JSONFormatter(logging.Formatter):
    """Custom formatter that outputs logs as JSON lines for easy parsing."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include extra fields from the record
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


def get_logger(name: str) -> Logger:
    """Get or create a configured logger with JSON formatting."""
    logger = logging.getLogger(name)

    # Only configure if handlers don't exist
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False

    return logger
