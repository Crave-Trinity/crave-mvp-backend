# File: app/config/logging.py
import logging
import os
from pythonjsonlogger import jsonlogger
from logging.handlers import RotatingFileHandler

# Environment-driven log level & file path
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/crave_trinity_backend.log")

def configure_logging() -> None:
    """
    Configure structured logging using JSON format,
    rotating files, and console output.
    """

    # Console handler (stdout)
    console_handler = logging.StreamHandler()
    console_formatter = jsonlogger.JsonFormatter(
        fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(LOG_LEVEL)

    # Rotating file handler
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

    # Apply basicConfig; replace any default handlers with ours
    logging.basicConfig(
        level=LOG_LEVEL,
        handlers=[console_handler, file_handler]
    )