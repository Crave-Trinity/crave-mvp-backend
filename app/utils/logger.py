# File: app/utils/logger.py
import logging
from app.config.logging import configure_logging

# Ensure logging config is applied when this module loads
configure_logging()

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with our preconfigured settings.
    """
    return logging.getLogger(name)