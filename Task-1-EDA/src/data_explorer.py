"""
data_explorer.py
-----------------
Performs structural exploration of the dataset: shape, dtypes, missing
values, duplicates, summary statistics, and categorical breakdowns.
This module answers the "what does the data look like?" questions that
should always precede deeper analysis.
"""

import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)


class DataExplorer:
    """Explores the structure and quality of a DataFrame."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def structural_overview(self) -> dict:
        """
        Returns:
            dict: shape, column dtypes, and memory usage of the dataset.
        """
        logger.info("Generating structural overview.")
        overview = {
            "n_rows": self.df.shape[0],
            "n_columns": self.df.shape[1],
            "columns": list(self.df.columns),
            "dtypes": self.df.dtypes.astype(str).to_dict(),
            "memory_usage_mb": round(self.df.memory_usage(deep=True).sum() / (1024 ** 2), 3),
        }
        return overview

    def missing_value_report(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: Count and percentage of missing values per column,
            sorted descending, for columns that have at least one missing value.
        """
        logger.info("Computing missing value report.")
        missing_count = self.df.isnull().sum()
        missing_pct = (missing_count / len(self.df)) * 100
        report = pd.DataFrame({
            "missing_count": missing_count,
            "missing_pct": missing_pct.round(2)
        })
        report = report[report["missing_count"] > 0].sort_values(
            "missing_count", ascending=False
        )
        return report

    def duplicate_report(self) -> dict:
        """
        Returns:
            dict: Number and percentage of fully duplicated rows.
        """
        logger.info("Checking for duplicate rows.")
        n_dupes = int(self.df.duplicated().sum())
        return {
            "duplicate_rows": n_dupes,
            "duplicate_pct": round((n_dupes / len(self.df)) * 100, 2),
        }

    def numeric_summary(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: Descriptive statistics (count, mean, std, min,
            quartiles, max) for all numeric columns.
        """
        logger.info("Computing numeric summary statistics.")
        return self.df.describe().T

    def categorical_summary(self) -> dict:
        """
        Returns:
            dict: For each categorical column, the value counts of its
            top categories.
        """
        logger.info("Computing categorical summaries.")
        cat_cols = self.df.select_dtypes(include=["object", "category"]).columns
        summary = {}
        for col in cat_cols:
            summary[col] = self.df[col].value_counts().head(10).to_dict()
        return summary

    def correlation_matrix(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: Pearson correlation matrix of numeric columns.
        """
        logger.info("Computing correlation matrix.")
        numeric_df = self.df.select_dtypes(include="number")
        return numeric_df.corr(numeric_only=True)

    def feature_relationships(self, category_col: str, numeric_cols=None) -> pd.DataFrame:
        """
        Summarize how numeric features vary across a categorical grouping,
        e.g. average revenue and rating per region.

        Args:
            category_col (str): Categorical column to group by.
            numeric_cols (list, optional): Numeric columns to aggregate.
                Defaults to all numeric columns.

        Returns:
            pd.DataFrame: Mean of each numeric column, grouped by category.
        """
        if category_col not in self.df.columns:
            logger.warning(f"feature_relationships: column '{category_col}' not found.")
            return pd.DataFrame()
        if numeric_cols is None:
            numeric_cols = self.df.select_dtypes(include="number").columns.tolist()
        numeric_cols = [c for c in numeric_cols if c in self.df.columns]
        logger.info(f"Computing feature relationships grouped by '{category_col}'.")
        return self.df.groupby(category_col)[numeric_cols].mean().round(2)

    def distribution_skew_kurtosis(self) -> pd.DataFrame:
        """
        Returns:
            pd.DataFrame: Skewness and kurtosis for every numeric column,
            useful for spotting non-normal distributions before modeling.
        """
        logger.info("Computing skewness and kurtosis for numeric columns.")
        numeric_df = self.df.select_dtypes(include="number")
        return pd.DataFrame({
            "skewness": numeric_df.skew().round(3),
            "kurtosis": numeric_df.kurt().round(3),
        })
