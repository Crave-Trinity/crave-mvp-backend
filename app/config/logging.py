# File: app/config/logging.py
import logging
import os
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler

# -- Sentry imports --
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# -- Environment-driven config --
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/crave_trinity_backend.log")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")  # Provide a DSN in your environment or leave blank

def configure_logging() -> None:
    """
    Configure JSON-structured logging, rotating file logs, console output,
    and optional Sentry error reporting (if SENTRY_DSN is provided).
    """

    # 1) Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(LOG_LEVEL)

    # 2) Rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=5 * 1024 * 1024,  # ~5MB per file
        backupCount=5
    )
    file_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(LOG_LEVEL)

    # 3) Configure Python's built-in logging
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=[console_handler, file_handler]
    )

    # 4) Optional: Initialize Sentry (only if SENTRY_DSN is set)
    if SENTRY_DSN:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,         # Capture INFO as breadcrumbs
            event_level=logging.ERROR   # Send errors as Sentry events
        )
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[sentry_logging],
            send_default_pii=True,      # Captures user IP & headers (optional)
        )
        logging.getLogger(__name__).info("Sentry SDK initialized with DSN.")