"""
data_loader.py
---------------
Handles loading and basic validation of the raw dataset.

Supports CSV, Excel (.xlsx/.xls), and JSON out of the box, and applies a set
of defensive checks (missing file, empty file, corrupted content, unsupported
format) so that a bad input fails fast with a clear message instead of
crashing deep inside the analysis pipeline.
"""

import os
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}


class DataLoadError(Exception):
    """Raised when the dataset cannot be loaded or is invalid."""
    pass


class DataLoader:
    """
    Responsible for reading the dataset from disk and performing
    lightweight structural validation before it is handed off to
    the rest of the pipeline.
    """

    def __init__(self, filepath: str, date_columns=None):
        """
        Args:
            filepath (str): Path to the dataset file (CSV, Excel, or JSON).
            date_columns (list[str], optional): Columns to parse as dates.
                Defaults to ["order_date"] for backward compatibility with
                the sample dataset; pass [] to disable date parsing.
        """
        self.filepath = filepath
        self.date_columns = ["order_date"] if date_columns is None else date_columns

    def load(self) -> pd.DataFrame:
        """
        Load the dataset from disk, auto-detecting the format from its
        file extension.

        Returns:
            pd.DataFrame: The loaded dataset.

        Raises:
            DataLoadError: If the file is missing, empty, unreadable,
                corrupted, or in an unsupported format.
        """
        logger.info(f"Attempting to load dataset from '{self.filepath}'")

        if not os.path.exists(self.filepath):
            logger.error(f"Dataset file not found: {self.filepath}")
            raise DataLoadError(f"Dataset file not found: {self.filepath}")

        if os.path.getsize(self.filepath) == 0:
            logger.error(f"Dataset file is empty on disk: {self.filepath}")
            raise DataLoadError(f"Dataset file is empty: {self.filepath}")

        ext = os.path.splitext(self.filepath)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            logger.error(f"Unsupported file format: {ext}")
            raise DataLoadError(
                f"Unsupported file format '{ext}'. "
                f"Supported formats: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
            )

        try:
            df = self._read(ext)
        except DataLoadError:
            raise
        except Exception as exc:
            logger.exception("Failed to parse the dataset file.")
            raise DataLoadError(
                f"Could not read file (it may be corrupted or malformed): {exc}"
            ) from exc

        if df.empty:
            logger.error("Loaded dataset has no rows.")
            raise DataLoadError("Loaded dataset is empty (0 rows).")

        if df.shape[1] == 0:
            logger.error("Loaded dataset has no columns.")
            raise DataLoadError("Loaded dataset has no columns.")

        logger.info(f"Dataset loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
        return df

    def _read(self, ext: str) -> pd.DataFrame:
        if ext == ".csv":
            # Peek at the header first so we only ask pandas to parse dates
            # for columns that actually exist (avoids a hard crash on
            # datasets that don't have an order_date column).
            header = pd.read_csv(self.filepath, nrows=0)
            present_date_cols = [c for c in self.date_columns if c in header.columns]
            return pd.read_csv(self.filepath, parse_dates=present_date_cols or None)
        elif ext in (".xlsx", ".xls"):
            df = pd.read_excel(self.filepath)
            present_date_cols = [c for c in self.date_columns if c in df.columns]
            for col in present_date_cols:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            return df
        elif ext == ".json":
            df = pd.read_json(self.filepath)
            present_date_cols = [c for c in self.date_columns if c in df.columns]
            for col in present_date_cols:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            return df
        raise DataLoadError(f"Unsupported file format '{ext}'.")
