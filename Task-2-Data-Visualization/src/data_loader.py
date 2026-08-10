"""
data_loader.py
---------------
Loads and validates the sales dataset used for visualization.
"""

import os
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)


class DataLoadError(Exception):
    """Raised when the dataset cannot be loaded or is invalid."""
    pass


class DataLoader:
    """Loads the dataset from disk, with validation and cleaning helpers."""

    def __init__(self, filepath: str):
        self.filepath = filepath

    def load(self, clean: bool = True) -> pd.DataFrame:
        """
        Load the dataset, optionally applying light cleaning so that
        visualizations are not distorted by obvious data issues.

        Args:
            clean (bool): If True, drop duplicates and clip invalid values.

        Returns:
            pd.DataFrame: The loaded (and optionally cleaned) dataset.
        """
        logger.info(f"Loading dataset from '{self.filepath}'")
        if not os.path.exists(self.filepath):
            logger.error(f"Dataset not found at {self.filepath}")
            raise DataLoadError(f"Dataset not found at {self.filepath}")

        try:
            df = pd.read_csv(self.filepath, parse_dates=["order_date"])
        except Exception as exc:
            logger.exception("Failed to read CSV.")
            raise DataLoadError(f"Could not read CSV: {exc}") from exc

        if df.empty:
            raise DataLoadError("Dataset is empty.")

        if clean:
            before = len(df)
            df = df.drop_duplicates()
            df = df[df["delivery_days"] > 0]
            df = df[df["unit_price"] > 0]
            after = len(df)
            logger.info(f"Cleaning removed {before - after} invalid/duplicate rows.")

        logger.info(f"Dataset ready: {df.shape[0]} rows, {df.shape[1]} columns.")
        return df
