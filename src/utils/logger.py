"""Centralized logging configuration."""

import logging
import sys
from pathlib import Path

from config.settings import settings


def setup_logger(name: str = "spotify_etl") -> logging.Logger:
    """
    Set up and configure a logger instance.

    Args:
        name: Name of the logger

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.app.log_level))

    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger

    # Create formatter
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.app.log_level))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler (only in production)
    if settings.app.environment == "production":
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(log_dir / "spotify_etl.log")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logger()

