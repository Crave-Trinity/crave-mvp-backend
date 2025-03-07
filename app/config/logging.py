# File: app/config/logging.py
import logging
import os
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/crave_trinity_backend.log")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")

def configure_logging() -> None:
    """
    Configure JSON logging, rotating file logs, console output,
    and optional Sentry error reporting (if SENTRY_DSN is set).
    """

    # 1) Make sure the logs/ directory exists
    log_dir = os.path.dirname(LOG_FILE_PATH)
    if log_dir:  # If there's a directory part
        os.makedirs(log_dir, exist_ok=True)

    # 2) Console handler
    console_handler = logging.StreamHandler()
    console_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(LOG_LEVEL)

    # 3) Rotating file handler
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=5
    )
    file_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(LOG_LEVEL)

    # 4) Basic logging config
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=[console_handler, file_handler]
    )

    # 5) Sentry integration (optional)
    if SENTRY_DSN:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,      # capture INFO+ as breadcrumbs
            event_level=logging.ERROR  # send ERROR+ as events
        )
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[sentry_logging],
            send_default_pii=True
        )
        logging.getLogger(__name__).info("Sentry SDK initialized.")