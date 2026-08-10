"""Tests for src/data_explorer.py"""

from src.data_explorer import DataExplorer


def test_structural_overview(sample_df):
    overview = DataExplorer(sample_df).structural_overview()

    assert overview["n_rows"] == len(sample_df)
    assert overview["n_columns"] == sample_df.shape[1]
    assert overview["memory_usage_mb"] > 0


def test_missing_value_report_flags_known_gaps(sample_df):
    report = DataExplorer(sample_df).missing_value_report()

    assert "customer_rating" in report.index
    assert "region" in report.index
    assert report.loc["customer_rating", "missing_count"] == 1


def test_missing_value_report_excludes_complete_columns(sample_df):
    report = DataExplorer(sample_df).missing_value_report()
    assert "order_id" not in report.index


def test_duplicate_report_detects_duplicate(sample_df):
    report = DataExplorer(sample_df).duplicate_report()
    assert report["duplicate_rows"] >= 1


def test_numeric_summary_includes_expected_columns(sample_df):
    summary = DataExplorer(sample_df).numeric_summary()
    assert "revenue" in summary.index
    assert "mean" in summary.columns


def test_categorical_summary_counts_categories(sample_df):
    summary = DataExplorer(sample_df).categorical_summary()
    assert "category" in summary
    assert sum(summary["category"].values()) <= len(sample_df)


def test_correlation_matrix_is_square(sample_df):
    corr = DataExplorer(sample_df).correlation_matrix()
    assert corr.shape[0] == corr.shape[1]
    # Diagonal of a correlation matrix is always 1.
    for col in corr.columns:
        assert round(corr.loc[col, col], 5) == 1.0


def test_feature_relationships_groups_by_category(sample_df):
    result = DataExplorer(sample_df).feature_relationships("category", ["revenue"])
    assert set(result.index) == set(sample_df["category"].unique())


def test_feature_relationships_missing_column_returns_empty(sample_df):
    result = DataExplorer(sample_df).feature_relationships("not_a_column")
    assert result.empty
