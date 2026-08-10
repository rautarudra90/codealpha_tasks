"""
logger_config.py
-----------------
Centralized logging configuration for the EDA project.

This module sets up a rotating file logger and a console logger so that
every module in the project can share the same consistent logging behaviour.
"""

import logging
import os
import time
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler

try:
    from config import LOGS_DIR, LOG_FILE_NAME
except ImportError:  # pragma: no cover - fallback if config.py isn't on path yet
    LOGS_DIR = "logs"
    LOG_FILE_NAME = "eda_project.log"


def get_logger(name: str, log_dir: str = LOGS_DIR, log_file: str = LOG_FILE_NAME) -> logging.Logger:
    """
    Create (or retrieve) a configured logger instance.

    Args:
        name (str): Name of the logger, typically __name__ of the calling module.
        log_dir (str): Directory where log files should be stored.
        log_file (str): Name of the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if the logger already exists.
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Rotating file handler: keeps logs from growing unbounded.
    file_handler = RotatingFileHandler(
        log_path, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Console handler for real-time feedback.
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


@contextmanager
def log_execution_time(logger: logging.Logger, task_name: str):
    """
    Context manager that logs how long a block of code took to run.

    Usage:
        with log_execution_time(logger, "Chart generation"):
            visualizer.generate_all()
    """
    start = time.perf_counter()
    logger.info(f"Started: {task_name}")
    try:
        yield
    except Exception:
        logger.exception(f"Failed: {task_name}")
        raise
    else:
        elapsed = time.perf_counter() - start
        logger.info(f"Finished: {task_name} (took {elapsed:.2f}s)")
