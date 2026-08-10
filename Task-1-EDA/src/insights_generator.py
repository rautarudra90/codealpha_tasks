"""
insights_generator.py
------------------------
Turns the numeric output of the EDA pipeline (correlations, group-bys,
outlier counts) into plain-English business insights and recommendations.
This is the layer that makes a report readable by someone who doesn't
want to interpret a correlation matrix themselves.

Every insight here is derived directly from the data passed in - nothing
is hardcoded to a specific dataset, so this module works for any tabular
dataset with a mix of numeric and categorical columns, and degrades
gracefully (skips a section) when expected columns aren't present.
"""

import pandas as pd
import numpy as np
from src.logger_config import get_logger

logger = get_logger(__name__)


class InsightsGenerator:
    """Generates plain-English insights and recommendations from EDA results."""

    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.insights = []

    def _add(self, text: str):
        self.insights.append(text)

    # ------------------------------------------------------------------
    # Insight builders
    # ------------------------------------------------------------------
    def category_performance(self, category_col: str, value_col: str):
        """Identify the best- and worst-performing category by a numeric value."""
        if category_col not in self.df.columns or value_col not in self.df.columns:
            return self
        grouped = self.df.groupby(category_col)[value_col].sum().sort_values(ascending=False)
        if grouped.empty:
            return self

        top, bottom = grouped.index[0], grouped.index[-1]
        top_val, bottom_val = grouped.iloc[0], grouped.iloc[-1]
        total = grouped.sum()
        top_share = (top_val / total * 100) if total else 0

        self._add(
            f"**{top}** is the strongest-performing {category_col.replace('_', ' ')}, "
            f"contributing {top_val:,.2f} in total {value_col.replace('_', ' ')} "
            f"({top_share:.1f}% of the total)."
        )
        if bottom != top:
            self._add(
                f"**{bottom}** is the weakest-performing {category_col.replace('_', ' ')}, "
                f"with only {bottom_val:,.2f} in total {value_col.replace('_', ' ')} — "
                f"consider investigating why it underperforms or whether it should be "
                f"deprioritized."
            )
        return self

    def correlation_highlights(self, correlation: pd.DataFrame, top_n: int = 2):
        """Surface the strongest positive and negative correlations."""
        if correlation is None or correlation.empty:
            return self

        pairs = []
        cols = correlation.columns
        for i, col_a in enumerate(cols):
            for col_b in cols[i + 1:]:
                value = correlation.loc[col_a, col_b]
                if pd.notna(value):
                    pairs.append((col_a, col_b, value))

        if not pairs:
            return self

        pairs.sort(key=lambda x: x[2], reverse=True)
        strongest_positive = [p for p in pairs if p[2] > 0][:top_n]
        strongest_negative = sorted([p for p in pairs if p[2] < 0], key=lambda x: x[2])[:top_n]

        for col_a, col_b, value in strongest_positive:
            if value > 0.3:
                self._add(
                    f"**{col_a}** and **{col_b}** show a positive correlation "
                    f"(r = {value:.2f}) — as one increases, the other tends to increase too."
                )
        for col_a, col_b, value in strongest_negative:
            if value < -0.3:
                self._add(
                    f"**{col_a}** and **{col_b}** show a negative correlation "
                    f"(r = {value:.2f}) — as one increases, the other tends to decrease."
                )
        if not strongest_positive and not strongest_negative:
            self._add(
                "No strong linear correlations (|r| > 0.3) were found between numeric "
                "features — relationships in this dataset may be non-linear or weak."
            )
        return self

    def trend_analysis(self, date_col: str, value_col: str):
        """Describe the overall trend of a numeric value over time."""
        if date_col not in self.df.columns or value_col not in self.df.columns:
            return self
        if not pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
            return self

        series = self.df.set_index(date_col)[value_col].resample("ME").sum().dropna()
        if len(series) < 2:
            return self

        first_half = series.iloc[: len(series) // 2].mean()
        second_half = series.iloc[len(series) // 2:].mean()
        if first_half == 0:
            return self

        change_pct = (second_half - first_half) / first_half * 100
        direction = "increased" if change_pct > 0 else "decreased"
        self._add(
            f"{value_col.replace('_', ' ').title()} has {direction} by roughly "
            f"{abs(change_pct):.1f}% comparing the first half of the time period to the second."
        )
        return self

    def outlier_summary(self, outlier_summary_df: pd.DataFrame):
        """Summarize which columns have the most outliers."""
        if outlier_summary_df is None or outlier_summary_df.empty:
            return self
        worst = outlier_summary_df.iloc[0]
        if worst["outlier_count"] > 0:
            self._add(
                f"**{worst['column']}** has the most outliers of any numeric column "
                f"({int(worst['outlier_count'])} rows, {worst['outlier_pct']}% of the data) — "
                f"worth reviewing before this field feeds into any model."
            )
        return self

    def data_quality_summary(self, missing_report: pd.DataFrame, duplicate_report: dict):
        """Summarize overall data quality for the recommendations section."""
        if missing_report is not None and not missing_report.empty:
            worst_col = missing_report.index[0]
            worst_pct = missing_report.iloc[0]["missing_pct"]
            self._add(
                f"**{worst_col}** has the highest missing-value rate ({worst_pct}%) — "
                f"decide whether to impute, drop, or flag these rows before modeling."
            )
        if duplicate_report and duplicate_report.get("duplicate_rows", 0) > 0:
            self._add(
                f"{duplicate_report['duplicate_rows']} duplicate rows "
                f"({duplicate_report['duplicate_pct']}%) were found in the raw data — "
                f"these should be removed during cleaning to avoid double-counting."
            )
        return self

    def recommendations(self) -> list:
        """Generate general, data-driven recommendations based on what was found."""
        recs = [
            "Clean and validate the flagged data quality issues before using this "
            "dataset for modeling or dashboards.",
            "Investigate the strongest correlations above to understand whether they "
            "reflect a causal relationship or are driven by a third factor.",
            "Review flagged outliers individually — some may be genuine high-value "
            "events worth understanding, not just noise to remove.",
        ]
        return recs

    # ------------------------------------------------------------------
    # Output
    # ------------------------------------------------------------------
    def get_insights(self) -> list:
        if not self.insights:
            return ["No significant patterns were detected with the checks run."]
        return self.insights

    def get_report_text(self) -> str:
        """Render all collected insights as a Markdown bullet list."""
        lines = [f"- {insight}" for insight in self.get_insights()]
        return "\n".join(lines)
