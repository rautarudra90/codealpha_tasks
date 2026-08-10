"""
hypothesis_tester.py
----------------------
Runs formal statistical hypothesis tests to validate assumptions about the
dataset (e.g. "Does discount percentage significantly affect revenue?",
"Do regions differ significantly in average revenue?").
"""

import pandas as pd
from scipy import stats
from src.logger_config import get_logger

logger = get_logger(__name__)


class HypothesisTester:
    """Performs statistical hypothesis tests on the dataset."""

    def __init__(self, df: pd.DataFrame, alpha: float = 0.05):
        """
        Args:
            df (pd.DataFrame): Dataset to test.
            alpha (float): Significance level used to accept/reject H0.
        """
        self.df = df
        self.alpha = alpha

    def test_anova_region_revenue(self) -> dict:
        """
        H0: Mean revenue is the same across all regions.
        H1: At least one region has a different mean revenue.

        Uses a one-way ANOVA test.

        Returns:
            dict: Test statistic, p-value, and conclusion.
        """
        logger.info("Running ANOVA: revenue across regions.")
        groups = [g["revenue"].dropna().values for _, g in self.df.groupby("region")]
        f_stat, p_value = stats.f_oneway(*groups)
        result = self._build_result(
            "One-Way ANOVA: revenue ~ region", f_stat, p_value
        )
        return result

    def test_correlation_price_rating(self) -> dict:
        """
        H0: There is no linear correlation between unit_price and customer_rating.
        H1: There is a significant linear correlation.

        Uses Pearson correlation test.

        Returns:
            dict: Correlation coefficient, p-value, and conclusion.
        """
        logger.info("Running Pearson correlation test: unit_price vs customer_rating.")
        subset = self.df[["unit_price", "customer_rating"]].dropna()
        corr, p_value = stats.pearsonr(subset["unit_price"], subset["customer_rating"])
        result = self._build_result(
            "Pearson correlation: unit_price vs customer_rating", corr, p_value
        )
        result["correlation_coefficient"] = round(corr, 4)
        return result

    def test_ttest_discounted_vs_full_price_revenue(self) -> dict:
        """
        H0: Mean revenue is equal for discounted vs full-price orders.
        H1: Mean revenue differs between discounted and full-price orders.

        Uses an independent two-sample t-test (Welch's, unequal variance).

        Returns:
            dict: Test statistic, p-value, and conclusion.
        """
        logger.info("Running t-test: discounted vs full-price revenue.")
        discounted = self.df[self.df["discount_pct"] > 0]["revenue"].dropna()
        full_price = self.df[self.df["discount_pct"] == 0]["revenue"].dropna()
        t_stat, p_value = stats.ttest_ind(discounted, full_price, equal_var=False)
        result = self._build_result(
            "Welch's t-test: discounted vs full-price revenue", t_stat, p_value
        )
        return result

    def test_chi_square_category_payment(self) -> dict:
        """
        H0: Product category and payment method are independent.
        H1: Product category and payment method are associated.

        Uses a Chi-Square test of independence.

        Returns:
            dict: Chi-square statistic, p-value, and conclusion.
        """
        logger.info("Running Chi-Square test: category vs payment_method.")
        contingency = pd.crosstab(self.df["category"], self.df["payment_method"])
        chi2, p_value, dof, _ = stats.chi2_contingency(contingency)
        result = self._build_result(
            "Chi-Square test: category vs payment_method", chi2, p_value
        )
        result["degrees_of_freedom"] = dof
        return result

    def run_all(self) -> list:
        """
        Run every hypothesis test and return a list of result dicts.
        Individual tests are skipped (not crashed on) if their required
        columns aren't present in the dataset, so this works across
        different datasets, not just the bundled sample.
        """
        logger.info("Running full hypothesis testing suite.")
        candidate_tests = [
            (self.test_anova_region_revenue, ["region", "revenue"]),
            (self.test_correlation_price_rating, ["unit_price", "customer_rating"]),
            (self.test_ttest_discounted_vs_full_price_revenue, ["discount_pct", "revenue"]),
            (self.test_chi_square_category_payment, ["category", "payment_method"]),
        ]
        results = []
        for test_fn, required_cols in candidate_tests:
            if not all(col in self.df.columns for col in required_cols):
                logger.info(f"Skipping {test_fn.__name__}: missing columns {required_cols}.")
                continue
            try:
                results.append(test_fn())
            except Exception:
                logger.exception(f"Hypothesis test {test_fn.__name__} failed; skipping it.")
        return results

    def _build_result(self, test_name: str, statistic: float, p_value: float) -> dict:
        significant = p_value < self.alpha
        conclusion = (
            "Reject H0 (statistically significant result)"
            if significant
            else "Fail to reject H0 (no significant evidence)"
        )
        result = {
            "test_name": test_name,
            "statistic": round(float(statistic), 4),
            "p_value": round(float(p_value), 6),
            "alpha": self.alpha,
            "significant": significant,
            "conclusion": conclusion,
        }
        logger.info(f"{test_name}: p={result['p_value']} -> {conclusion}")
        return result
