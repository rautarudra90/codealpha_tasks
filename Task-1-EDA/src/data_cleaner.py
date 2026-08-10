"""
data_cleaner.py
-----------------
Dedicated data-cleaning pipeline. Runs after DataLoader and before
DataExplorer/AnomalyDetector/HypothesisTester, so downstream analysis
always works on validated, standardized data instead of raw input.

Each cleaning step is a small, independent method that mutates an internal
copy of the DataFrame and records what it did in self.report, so the whole
pipeline stays inspectable and testable in isolation.
"""

import re
import numpy as np
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)


class DataCleaner:
    """Cleans a DataFrame and produces a structured report of every change made."""

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.original_shape = df.shape
        self.report = {
            "duplicates_removed": 0,
            "missing_values_before": {},
            "missing_values_handled": {},
            "dtype_fixes": {},
            "columns_renamed": {},
            "dates_converted": [],
            "outliers_capped": {},
            "final_shape": None,
        }

    # ------------------------------------------------------------------
    # Individual cleaning steps
    # ------------------------------------------------------------------
    def remove_duplicates(self) -> "DataCleaner":
        """Drop fully duplicated rows."""
        before = len(self.df)
        self.df = self.df.drop_duplicates()
        removed = before - len(self.df)
        self.report["duplicates_removed"] = removed
        if removed:
            logger.info(f"Removed {removed} duplicate rows.")
        return self

    def standardize_column_names(self) -> "DataCleaner":
        """Convert column names to consistent snake_case, stripped of whitespace."""
        renamed = {}
        new_columns = []
        for col in self.df.columns:
            # Any run of non-alphanumeric characters (spaces, hyphens,
            # parentheses, currency symbols, etc.) becomes a single
            # underscore, rather than being silently deleted - so
            # "Unit-Price ($)" becomes "unit_price", not "unitprice".
            clean = re.sub(r"[^0-9a-zA-Z]+", "_", str(col).strip()).strip("_").lower()
            new_columns.append(clean)
            if clean != col:
                renamed[col] = clean
        self.df.columns = new_columns
        self.report["columns_renamed"] = renamed
        if renamed:
            logger.info(f"Standardized {len(renamed)} column name(s).")
        return self

    def detect_and_fix_dtypes(self) -> "DataCleaner":
        """
        Detect object columns that are actually numeric (e.g. '$1,200' or
        '45%' stored as text) and convert them where it's safe to do so.
        """
        fixes = {}
        for col in self.df.select_dtypes(include="object").columns:
            sample = self.df[col].dropna().astype(str).head(200)
            if sample.empty:
                continue
            cleaned = sample.str.replace(r"[$,%\s]", "", regex=True)
            numeric_like = pd.to_numeric(cleaned, errors="coerce")
            # Only convert if the vast majority of non-null values parse cleanly.
            if numeric_like.notna().mean() > 0.95:
                full_clean = (
                    self.df[col].astype(str).str.replace(r"[$,%\s]", "", regex=True)
                )
                converted = pd.to_numeric(full_clean, errors="coerce")
                self.df[col] = converted
                fixes[col] = "object -> numeric"
        self.report["dtype_fixes"] = fixes
        if fixes:
            logger.info(f"Fixed data types for columns: {list(fixes.keys())}")
        return self

    def convert_dates(self, date_columns=None) -> "DataCleaner":
        """
        Convert likely date columns to proper datetime dtype. If date_columns
        is not given, any column whose name contains 'date' or 'time' is
        treated as a candidate.
        """
        if date_columns is None:
            date_columns = [
                c for c in self.df.columns if re.search(r"date|time", c, re.IGNORECASE)
            ]
        converted = []
        for col in date_columns:
            if col not in self.df.columns:
                continue
            if not pd.api.types.is_datetime64_any_dtype(self.df[col]):
                parsed = pd.to_datetime(self.df[col], errors="coerce")
                # Only commit the conversion if most values actually parsed.
                if parsed.notna().mean() > 0.8:
                    self.df[col] = parsed
                    converted.append(col)
        self.report["dates_converted"] = converted
        if converted:
            logger.info(f"Converted to datetime: {converted}")
        return self

    def handle_missing_values(self, numeric_strategy="median", categorical_strategy="mode") -> "DataCleaner":
        """
        Fill missing values.

        Args:
            numeric_strategy (str): "median", "mean", or "zero".
            categorical_strategy (str): "mode" or "unknown".
        """
        before = self.df.isnull().sum()
        self.report["missing_values_before"] = before[before > 0].to_dict()

        handled = {}
        for col in self.df.columns:
            n_missing = self.df[col].isnull().sum()
            if n_missing == 0:
                continue

            if pd.api.types.is_numeric_dtype(self.df[col]):
                if numeric_strategy == "mean":
                    fill_value = self.df[col].mean()
                elif numeric_strategy == "zero":
                    fill_value = 0
                else:
                    fill_value = self.df[col].median()
                self.df[col] = self.df[col].fillna(fill_value)
                handled[col] = f"filled {n_missing} with {numeric_strategy} ({round(float(fill_value), 3)})"

            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                self.df[col] = self.df[col].ffill().bfill()
                handled[col] = f"filled {n_missing} via forward/backward fill"

            else:
                if categorical_strategy == "unknown":
                    fill_value = "Unknown"
                else:
                    mode = self.df[col].mode()
                    fill_value = mode.iloc[0] if not mode.empty else "Unknown"
                self.df[col] = self.df[col].fillna(fill_value)
                handled[col] = f"filled {n_missing} with '{fill_value}'"

        self.report["missing_values_handled"] = handled
        if handled:
            logger.info(f"Handled missing values in {len(handled)} column(s).")
        return self

    def handle_outliers(self, columns=None, method="cap", k: float = 1.5) -> "DataCleaner":
        """
        Handle outliers in numeric columns using the IQR method.

        Args:
            columns (list[str], optional): Columns to process. Defaults to
                all numeric columns.
            method (str): "cap" clips values to the IQR fence (winsorizing,
                preserves row count); "remove" drops offending rows.
            k (float): IQR multiplier.
        """
        if columns is None:
            columns = self.df.select_dtypes(include=np.number).columns.tolist()

        capped_counts = {}
        for col in columns:
            if col not in self.df.columns:
                continue
            series = self.df[col].dropna()
            if series.empty:
                continue
            q1, q3 = series.quantile(0.25), series.quantile(0.75)
            iqr = q3 - q1
            lower, upper = q1 - k * iqr, q3 + k * iqr

            if method == "remove":
                mask = (self.df[col] < lower) | (self.df[col] > upper)
                capped_counts[col] = int(mask.sum())
                self.df = self.df[~mask]
            else:
                below = (self.df[col] < lower).sum()
                above = (self.df[col] > upper).sum()
                self.df[col] = self.df[col].clip(lower=lower, upper=upper)
                capped_counts[col] = int(below + above)

        self.report["outliers_capped"] = {k_: v for k_, v in capped_counts.items() if v > 0}
        if self.report["outliers_capped"]:
            logger.info(f"Outlier handling ({method}): {self.report['outliers_capped']}")
        return self

    def optimize_memory(self) -> "DataCleaner":
        """
        Downcast numeric columns to the smallest safe dtype (e.g. int64 -> int32,
        float64 -> float32) and convert low-cardinality object columns to
        'category' dtype. This is a vectorized, one-pass operation that can
        meaningfully cut memory usage on large datasets without changing values.
        """
        before_mb = self.df.memory_usage(deep=True).sum() / (1024 ** 2)

        for col in self.df.select_dtypes(include="integer").columns:
            self.df[col] = pd.to_numeric(self.df[col], downcast="integer")
        for col in self.df.select_dtypes(include="float").columns:
            self.df[col] = pd.to_numeric(self.df[col], downcast="float")
        for col in self.df.select_dtypes(include="object").columns:
            n_unique = self.df[col].nunique(dropna=True)
            if n_unique > 0 and n_unique / len(self.df) < 0.5:
                self.df[col] = self.df[col].astype("category")

        after_mb = self.df.memory_usage(deep=True).sum() / (1024 ** 2)
        self.report["memory_optimization_mb"] = {
            "before": round(before_mb, 3), "after": round(after_mb, 3),
            "reduction_pct": round((1 - after_mb / before_mb) * 100, 1) if before_mb else 0,
        }
        logger.info(
            f"Memory optimized: {before_mb:.2f}MB -> {after_mb:.2f}MB "
            f"({self.report['memory_optimization_mb']['reduction_pct']}% reduction)"
        )
        return self

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------
    def run_full_cleaning(
        self,
        numeric_strategy="median",
        categorical_strategy="mode",
        outlier_method="cap",
    ) -> "DataCleaner":
        """Run the standard cleaning sequence end to end."""
        logger.info("Starting full data cleaning pipeline.")
        (
            self.standardize_column_names()
            .remove_duplicates()
            .detect_and_fix_dtypes()
            .convert_dates()
            .handle_missing_values(numeric_strategy, categorical_strategy)
            .handle_outliers(method=outlier_method)
            .optimize_memory()
        )
        self.report["final_shape"] = self.df.shape
        logger.info(
            f"Cleaning complete: {self.original_shape} -> {self.df.shape}"
        )
        return self

    def get_cleaned_data(self) -> pd.DataFrame:
        return self.df

    def get_report(self) -> dict:
        if self.report["final_shape"] is None:
            self.report["final_shape"] = self.df.shape
        self.report["original_shape"] = self.original_shape
        return self.report
