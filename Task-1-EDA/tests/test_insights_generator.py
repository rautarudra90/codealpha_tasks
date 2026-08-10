"""Tests for src/insights_generator.py"""

from src.insights_generator import InsightsGenerator
from src.data_explorer import DataExplorer


def test_category_performance_identifies_top_and_bottom(sample_df):
    generator = InsightsGenerator(sample_df).category_performance("category", "revenue")
    text = generator.get_report_text()

    assert "strongest-performing" in text
    assert "category" in text.lower() or any(
        cat in text for cat in sample_df["category"].unique()
    )


def test_correlation_highlights_handles_empty_matrix(sample_df):
    generator = InsightsGenerator(sample_df).correlation_highlights(None)
    # Should not raise, and should return no crash-causing state.
    assert isinstance(generator.get_insights(), list)


def test_data_quality_summary_mentions_missing_and_duplicates(sample_df):
    explorer = DataExplorer(sample_df)
    missing = explorer.missing_value_report()
    duplicates = explorer.duplicate_report()

    generator = InsightsGenerator(sample_df).data_quality_summary(missing, duplicates)
    text = generator.get_report_text()

    assert "duplicate" in text.lower() or "missing" in text.lower()


def test_get_insights_returns_fallback_when_nothing_found():
    import pandas as pd
    empty_df = pd.DataFrame({"a": [1, 2, 3]})
    generator = InsightsGenerator(empty_df)

    insights = generator.get_insights()
    assert len(insights) == 1
    assert "No significant patterns" in insights[0]


def test_recommendations_returns_non_empty_list(sample_df):
    generator = InsightsGenerator(sample_df)
    recs = generator.recommendations()
    assert len(recs) >= 1
