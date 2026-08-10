"""Tests for src/hypothesis_tester.py"""

from src.hypothesis_tester import HypothesisTester


def test_ttest_returns_expected_keys(sample_df):
    tester = HypothesisTester(sample_df)
    result = tester.test_ttest_discounted_vs_full_price_revenue()

    assert set(["test_name", "statistic", "p_value", "alpha", "significant", "conclusion"]).issubset(result)
    assert result["alpha"] == 0.05


def test_significance_flag_matches_pvalue(sample_df):
    tester = HypothesisTester(sample_df, alpha=0.05)
    result = tester.test_chi_square_category_payment()

    assert result["significant"] == (result["p_value"] < 0.05)


def test_run_all_skips_tests_with_missing_columns(sample_df):
    df = sample_df.drop(columns=["region"])
    tester = HypothesisTester(df)
    results = tester.run_all()

    test_names = [r["test_name"] for r in results]
    assert not any("region" in name for name in test_names)
    # The other three tests should still run fine.
    assert len(results) == 3


def test_run_all_on_full_dataset_runs_all_four(sample_df):
    tester = HypothesisTester(sample_df)
    results = tester.run_all()
    assert len(results) == 4
