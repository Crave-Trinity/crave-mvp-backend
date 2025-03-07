# File: app/config/logging.py
import logging
import os
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Logging configuration from environment variables
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/crave_trinity_backend.log")
SENTRY_DSN = os.getenv("SENTRY_DSN", "")

# Sentry-specific settings
# Set the environment: use "production", "staging", or "development" as needed.
SENTRY_ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
# Set a release version; increment this manually with significant revisions.
SENTRY_RELEASE = os.getenv("SENTRY_RELEASE", "crave_backend@1.0")
# Optionally enable performance tracing by setting a sample rate (0.0 to disable)
SENTRY_TRACES_SAMPLE_RATE = float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "1.0"))

def configure_logging() -> None:
    """
    Configure JSON-structured logging with console and rotating file outputs,
    and initialize Sentry error reporting with environment, release, and optional performance tracing.
    """
    # Ensure the logs/ directory exists
    log_dir = os.path.dirname(LOG_FILE_PATH)
    if log_dir:
        os.makedirs(log_dir, exist_ok=True)

    # Setup console handler for real-time logs
    console_handler = logging.StreamHandler()
    console_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(LOG_LEVEL)

    # Setup rotating file handler to persist logs
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH,
        maxBytes=5 * 1024 * 1024,  # 5MB per file
        backupCount=5
    )
    file_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(LOG_LEVEL)

    # Apply basic logging configuration
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=[console_handler, file_handler]
    )

    # Initialize Sentry if DSN is provided
    if SENTRY_DSN:
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture INFO-level logs as breadcrumbs
            event_level=logging.ERROR  # Send ERROR-level logs as Sentry events
        )
        sentry_sdk.init(
            dsn=SENTRY_DSN,
            integrations=[sentry_logging],
            send_default_pii=True,
            environment=SENTRY_ENVIRONMENT,
            release=SENTRY_RELEASE,
            traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE  # Set to 0.0 to disable performance tracing
        )
        logging.getLogger(__name__).info(
            "Sentry SDK initialized with DSN, environment, and release."
        )