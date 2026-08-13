"""
data_loader.py
---------------
Loads and validates the raw text dataset used for sentiment analysis.
"""

import os
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)


class DataLoadError(Exception):
    """Raised when the dataset cannot be loaded or is invalid."""
    pass


class DataLoader:
    """Loads the review/text dataset from disk with validation."""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self) -> pd.DataFrame:
        """
        Load the dataset from disk.

        Returns:
            pd.DataFrame: The loaded dataset.

        Raises:
            DataLoadError: If the file is missing, empty, or unreadable.
        """
        logger.info(f"Loading dataset from '{self.filepath}'")

        if not os.path.exists(self.filepath):
            logger.error(f"Dataset not found: {self.filepath}")
            raise DataLoadError(f"Dataset not found: {self.filepath}")

        try:
            df = pd.read_csv(self.filepath, parse_dates=["review_date"])
        except Exception as exc:
            logger.exception("Failed to parse CSV.")
            raise DataLoadError(f"Could not read CSV: {exc}") from exc

        if df.empty:
            raise DataLoadError("Dataset is empty.")

        if "text" not in df.columns:
            raise DataLoadError("Dataset must contain a 'text' column.")

        logger.info(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df
