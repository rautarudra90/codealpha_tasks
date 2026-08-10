"""
logger_config.py
-----------------
Centralized logging configuration shared across the data visualization project.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def get_logger(name: str, log_dir: str = "logs", log_file: str = "visualization_project.log") -> logging.Logger:
    """
    Create or retrieve a configured logger.

    Args:
        name (str): Logger name, typically __name__.
        log_dir (str): Directory for log files.
        log_file (str): Log file name.

    Returns:
        logging.Logger: Configured logger.
    """
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, log_file)

    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(log_path, maxBytes=2 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    return logger
