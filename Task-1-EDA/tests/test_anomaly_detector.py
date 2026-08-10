"""Tests for src/anomaly_detector.py"""

from src.anomaly_detector import AnomalyDetector


def test_iqr_outliers_finds_injected_outlier(sample_df):
    outliers = AnomalyDetector(sample_df).iqr_outliers("revenue")
    assert 999999.0 in outliers["revenue"].values


def test_zscore_outliers_finds_injected_outlier(sample_df):
    outliers = AnomalyDetector(sample_df).zscore_outliers("revenue", threshold=2.0)
    assert 999999.0 in outliers["revenue"].values


def test_zscore_handles_zero_variance_column(sample_df):
    df = sample_df.copy()
    df["constant"] = 5
    outliers = AnomalyDetector(df).zscore_outliers("constant")
    assert outliers.empty


def test_isolation_forest_returns_dataframe(sample_df):
    outliers = AnomalyDetector(sample_df).isolation_forest_outliers(
        columns=["revenue", "unit_price", "customer_age"]
    )
    assert isinstance(outliers.index, type(sample_df.index))
    assert len(outliers) < len(sample_df)


def test_logical_anomalies_detects_invalid_rating(sample_df):
    df = sample_df.copy()
    df.loc[0, "customer_rating"] = 7.0  # out of 1-5 range
    anomalies = AnomalyDetector(df).logical_anomalies()
    assert "out_of_range_rating" in anomalies


def test_summary_returns_one_row_per_column(sample_df):
    detector = AnomalyDetector(sample_df)
    summary = detector.summary(numeric_columns=["revenue", "unit_price"])
    assert set(summary["column"]) == {"revenue", "unit_price"}


def test_compare_methods_includes_all_three(sample_df):
    detector = AnomalyDetector(sample_df)
    comparison = detector.compare_methods(numeric_columns=["revenue", "unit_price"])
    assert "iqr_outliers" in comparison.columns
    assert "zscore_outliers" in comparison.columns
    assert "isolation_forest_flagged_total" in comparison.columns
