"""
anomaly_detector.py
---------------------
Detects data quality issues and statistical anomalies/outliers within the
dataset using three complementary methods:

    1. IQR (Tukey fences)      - robust, univariate, good default.
    2. Z-score                 - assumes near-normal distribution, univariate.
    3. Isolation Forest        - multivariate, catches anomalies that only
                                  show up as unusual *combinations* of values.

A `compare_methods` helper runs all three side by side so the differences
between them are visible instead of hidden behind a single "the" outlier
count. Domain-logic sanity checks (e.g. negative delivery days) remain as
a separate, rule-based layer since no statistical method can infer business
rules from the data alone.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from src.logger_config import get_logger

try:
    from config import RANDOM_STATE, IQR_MULTIPLIER, ZSCORE_THRESHOLD, ISOLATION_FOREST_CONTAMINATION
except ImportError:  # pragma: no cover
    RANDOM_STATE, IQR_MULTIPLIER, ZSCORE_THRESHOLD, ISOLATION_FOREST_CONTAMINATION = 42, 1.5, 3.0, 0.02

logger = get_logger(__name__)


class AnomalyDetector:
    """Detects outliers and logically invalid values in the dataset."""

    def __init__(self, df: pd.DataFrame):
        self.df = df

    # ------------------------------------------------------------------
    # IQR method
    # ------------------------------------------------------------------
    def iqr_outliers(self, column: str, k: float = IQR_MULTIPLIER) -> pd.DataFrame:
        """
        Detect outliers in a numeric column using the Interquartile Range (IQR) method.

        Args:
            column (str): Column to analyze.
            k (float): IQR multiplier (1.5 = standard, 3.0 = extreme outliers only).

        Returns:
            pd.DataFrame: Subset of rows considered outliers for this column.
        """
        logger.info(f"Detecting IQR outliers for column '{column}'.")
        series = self.df[column].dropna()
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr

        outliers = self.df[(self.df[column] < lower_bound) | (self.df[column] > upper_bound)]
        logger.info(
            f"Column '{column}': {len(outliers)} IQR outliers found "
            f"(bounds: [{lower_bound:.2f}, {upper_bound:.2f}])"
        )
        return outliers

    # ------------------------------------------------------------------
    # Z-score method
    # ------------------------------------------------------------------
    def zscore_outliers(self, column: str, threshold: float = ZSCORE_THRESHOLD) -> pd.DataFrame:
        """
        Detect outliers using the standard score: how many standard
        deviations a value sits from the column mean.

        Args:
            column (str): Column to analyze.
            threshold (float): |z| above this value is flagged.

        Returns:
            pd.DataFrame: Subset of rows considered outliers for this column.
        """
        logger.info(f"Detecting Z-score outliers for column '{column}'.")
        series = self.df[column]
        std = series.std()
        if not std or np.isnan(std):
            return self.df.iloc[0:0]
        z_scores = (series - series.mean()) / std
        outliers = self.df[z_scores.abs() > threshold]
        logger.info(f"Column '{column}': {len(outliers)} Z-score outliers found (threshold={threshold}).")
        return outliers

    # ------------------------------------------------------------------
    # Isolation Forest (multivariate)
    # ------------------------------------------------------------------
    def isolation_forest_outliers(
        self, columns=None, contamination: float = ISOLATION_FOREST_CONTAMINATION
    ) -> pd.DataFrame:
        """
        Detect multivariate anomalies using Isolation Forest. Unlike IQR or
        Z-score, this considers combinations of columns at once, so it can
        flag a row that looks normal on every single feature but unusual
        as a whole (e.g. a high price paired with a very short delivery time).

        Args:
            columns (list[str], optional): Numeric columns to use as features.
                Defaults to all numeric columns.
            contamination (float): Expected proportion of anomalies (0-0.5).

        Returns:
            pd.DataFrame: Subset of rows flagged as anomalies.
        """
        if columns is None:
            columns = self.df.select_dtypes(include=np.number).columns.tolist()
        columns = [c for c in columns if c in self.df.columns]
        if not columns:
            logger.warning("No numeric columns available for Isolation Forest.")
            return self.df.iloc[0:0]

        logger.info(f"Running Isolation Forest on columns: {columns}")
        feature_df = self.df[columns].dropna()
        if feature_df.empty:
            return self.df.iloc[0:0]

        model = IsolationForest(
            contamination=contamination, random_state=RANDOM_STATE, n_estimators=200
        )
        predictions = model.fit_predict(feature_df)
        anomaly_index = feature_df.index[predictions == -1]

        outliers = self.df.loc[anomaly_index]
        logger.info(f"Isolation Forest flagged {len(outliers)} multivariate anomalies.")
        return outliers

    # ------------------------------------------------------------------
    # Domain-logic checks
    # ------------------------------------------------------------------
    def logical_anomalies(self) -> dict:
        """
        Apply domain-specific sanity checks that a pure statistical method
        would not catch (e.g. negative delivery days, ratings outside 1-5).

        Returns:
            dict: Mapping of anomaly description -> DataFrame of offending rows.
        """
        logger.info("Running domain-logic anomaly checks.")
        anomalies = {}

        if "delivery_days" in self.df.columns:
            invalid_delivery = self.df[self.df["delivery_days"] <= 0]
            if not invalid_delivery.empty:
                anomalies["non_positive_delivery_days"] = invalid_delivery

        if "customer_rating" in self.df.columns:
            invalid_rating = self.df[
                (self.df["customer_rating"] < 1) | (self.df["customer_rating"] > 5)
            ]
            if not invalid_rating.empty:
                anomalies["out_of_range_rating"] = invalid_rating

        if "unit_price" in self.df.columns:
            invalid_price = self.df[self.df["unit_price"] <= 0]
            if not invalid_price.empty:
                anomalies["non_positive_price"] = invalid_price

        for key, frame in anomalies.items():
            logger.info(f"Anomaly '{key}': {len(frame)} rows flagged.")

        return anomalies

    # ------------------------------------------------------------------
    # Summaries / comparisons
    # ------------------------------------------------------------------
    def summary(self, numeric_columns=None) -> pd.DataFrame:
        """
        Build a compact summary table of IQR-based outlier counts across
        multiple numeric columns.

        Args:
            numeric_columns (list, optional): Columns to check. Defaults to
                all numeric columns in the dataset.

        Returns:
            pd.DataFrame: One row per column with outlier counts and percentage.
        """
        if numeric_columns is None:
            numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()

        rows = []
        for col in numeric_columns:
            if col not in self.df.columns:
                continue
            outliers = self.iqr_outliers(col)
            rows.append({
                "column": col,
                "outlier_count": len(outliers),
                "outlier_pct": round((len(outliers) / len(self.df)) * 100, 2),
            })
        return pd.DataFrame(rows).sort_values("outlier_count", ascending=False)

    def compare_methods(self, numeric_columns=None) -> pd.DataFrame:
        """
        Run IQR, Z-score, and Isolation Forest side by side so their outlier
        counts can be compared directly for the same set of columns.

        Returns:
            pd.DataFrame: One row per column with a count from each method,
            plus one summary row for the multivariate Isolation Forest result.
        """
        if numeric_columns is None:
            numeric_columns = self.df.select_dtypes(include=np.number).columns.tolist()
        numeric_columns = [c for c in numeric_columns if c in self.df.columns]

        rows = []
        for col in numeric_columns:
            rows.append({
                "column": col,
                "iqr_outliers": len(self.iqr_outliers(col)),
                "zscore_outliers": len(self.zscore_outliers(col)),
            })
        comparison = pd.DataFrame(rows)

        iso_outliers = self.isolation_forest_outliers(numeric_columns)
        comparison["isolation_forest_flagged_total"] = len(iso_outliers)
        logger.info("Anomaly method comparison complete.")
        return comparison
