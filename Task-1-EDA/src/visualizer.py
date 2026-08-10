"""
visualizer.py
--------------
Generates a professional suite of exploratory visualizations - histograms,
scatter plots, box/violin plots, correlation heatmap, pair plot, count
plots, pie charts, and time trends - and saves them as PNG files into the
output directory. Every chart method is independent and defensive: it
checks that the columns it needs exist before drawing anything, so calling
`generate_all()` on a dataset that doesn't have every expected column
degrades gracefully instead of crashing.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend, safe for headless execution.
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from tqdm import tqdm
from src.logger_config import get_logger

try:
    from config import CHART_DPI, CHART_STYLE, CHART_PALETTE
except ImportError:  # pragma: no cover
    CHART_DPI, CHART_STYLE, CHART_PALETTE = 150, "whitegrid", "viridis"

logger = get_logger(__name__)
sns.set_theme(style=CHART_STYLE)


class EDAVisualizer:
    """Creates and saves EDA charts for the dataset."""

    def __init__(self, df: pd.DataFrame, output_dir: str = "output"):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _save(self, fig, filename: str):
        path = os.path.join(self.output_dir, filename)
        fig.savefig(path, bbox_inches="tight", dpi=CHART_DPI)
        plt.close(fig)
        logger.info(f"Saved chart: {path}")
        return path

    def _has_columns(self, *columns) -> bool:
        missing = [c for c in columns if c not in self.df.columns]
        if missing:
            logger.warning(f"Skipping chart - missing column(s): {missing}")
            return False
        return True

    # ------------------------------------------------------------------
    # Distribution charts
    # ------------------------------------------------------------------
    def plot_revenue_distribution(self, column: str = "revenue"):
        if not self._has_columns(column):
            return None
        fig, ax = plt.subplots(figsize=(8, 5))
        clipped = self.df[column].clip(upper=self.df[column].quantile(0.99))
        sns.histplot(clipped, bins=40, kde=True, ax=ax, color="#2E86AB")
        ax.set_title(f"{column.replace('_', ' ').title()} Distribution (99th percentile clipped)")
        ax.set_xlabel(column.replace("_", " ").title())
        return self._save(fig, f"{column}_distribution.png")

    def plot_boxplot_by_category(self, category_col: str = "category", value_col: str = "revenue"):
        if not self._has_columns(category_col, value_col):
            return None
        fig, ax = plt.subplots(figsize=(9, 5))
        order = self.df.groupby(category_col)[value_col].median().sort_values(ascending=False).index
        sns.boxplot(data=self.df, x=category_col, y=value_col, order=order, ax=ax,
                    showfliers=False, hue=category_col, palette=CHART_PALETTE, legend=False)
        ax.set_title(f"{value_col.replace('_', ' ').title()} Distribution by {category_col.replace('_', ' ').title()}")
        ax.tick_params(axis="x", rotation=30)
        return self._save(fig, f"{value_col}_by_{category_col}_boxplot.png")

    def plot_violin_by_category(self, category_col: str = "category", value_col: str = "revenue"):
        if not self._has_columns(category_col, value_col):
            return None
        fig, ax = plt.subplots(figsize=(9, 5))
        order = self.df.groupby(category_col)[value_col].median().sort_values(ascending=False).index
        sns.violinplot(data=self.df, x=category_col, y=value_col, order=order, ax=ax,
                        hue=category_col, palette=CHART_PALETTE, legend=False)
        ax.set_title(f"{value_col.replace('_', ' ').title()} Density by {category_col.replace('_', ' ').title()}")
        ax.tick_params(axis="x", rotation=30)
        return self._save(fig, f"{value_col}_by_{category_col}_violin.png")

    # ------------------------------------------------------------------
    # Relationship charts
    # ------------------------------------------------------------------
    def plot_correlation_heatmap(self):
        numeric_df = self.df.select_dtypes(include="number")
        if numeric_df.shape[1] < 2:
            logger.warning("Skipping correlation heatmap - fewer than 2 numeric columns.")
            return None
        fig, ax = plt.subplots(figsize=(8, 6))
        corr = numeric_df.corr(numeric_only=True)
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
        ax.set_title("Correlation Heatmap of Numeric Features")
        return self._save(fig, "correlation_heatmap.png")

    def plot_scatter(self, x_col: str = "customer_age", y_col: str = "customer_rating", hue_col: str = "category"):
        if not self._has_columns(x_col, y_col):
            return None
        fig, ax = plt.subplots(figsize=(8, 5))
        sample = self.df.sample(min(1000, len(self.df)), random_state=1)
        hue = hue_col if hue_col in self.df.columns else None
        sns.scatterplot(data=sample, x=x_col, y=y_col, hue=hue, alpha=0.6, ax=ax, legend=False)
        ax.set_title(f"{x_col.replace('_', ' ').title()} vs {y_col.replace('_', ' ').title()} (sampled)")
        return self._save(fig, f"{x_col}_vs_{y_col}_scatter.png")

    def plot_pairplot(self, columns=None, hue_col: str = None, sample_size: int = 500):
        numeric_df = self.df.select_dtypes(include="number")
        if columns is None:
            columns = numeric_df.columns.tolist()[:5]  # cap for readability/performance
        columns = [c for c in columns if c in self.df.columns]
        if len(columns) < 2:
            logger.warning("Skipping pair plot - fewer than 2 usable numeric columns.")
            return None
        sample = self.df.sample(min(sample_size, len(self.df)), random_state=1)
        hue = hue_col if hue_col in self.df.columns else None
        grid = sns.pairplot(sample, vars=columns, hue=hue, corner=True, diag_kind="kde")
        grid.figure.suptitle("Pairwise Feature Relationships", y=1.02)
        path = os.path.join(self.output_dir, "pairplot.png")
        grid.savefig(path, bbox_inches="tight", dpi=CHART_DPI)
        plt.close(grid.figure)
        logger.info(f"Saved chart: {path}")
        return path

    # ------------------------------------------------------------------
    # Categorical charts
    # ------------------------------------------------------------------
    def plot_count(self, column: str = "region"):
        if not self._has_columns(column):
            return None
        fig, ax = plt.subplots(figsize=(7, 5))
        counts = self.df[column].value_counts()
        sns.barplot(x=counts.index, y=counts.values, ax=ax, hue=counts.index,
                    palette="mako", legend=False)
        ax.set_title(f"Record Count by {column.replace('_', ' ').title()}")
        ax.set_ylabel("Count")
        ax.tick_params(axis="x", rotation=30)
        return self._save(fig, f"{column}_countplot.png")

    def plot_pie(self, column: str = "payment_method", top_n: int = 6):
        if not self._has_columns(column):
            return None
        counts = self.df[column].value_counts().head(top_n)
        fig, ax = plt.subplots(figsize=(7, 7))
        ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%",
               colors=sns.color_palette(CHART_PALETTE, len(counts)))
        ax.set_title(f"Share of Records by {column.replace('_', ' ').title()}")
        return self._save(fig, f"{column}_pie.png")

    def plot_bar_aggregate(self, category_col: str = "category", value_col: str = "revenue", agg: str = "sum"):
        if not self._has_columns(category_col, value_col):
            return None
        grouped = self.df.groupby(category_col)[value_col].agg(agg).sort_values(ascending=False)
        fig, ax = plt.subplots(figsize=(9, 5))
        sns.barplot(x=grouped.index, y=grouped.values, ax=ax, hue=grouped.index,
                    palette=CHART_PALETTE, legend=False)
        ax.set_title(f"{agg.title()} {value_col.replace('_', ' ').title()} by {category_col.replace('_', ' ').title()}")
        ax.tick_params(axis="x", rotation=30)
        return self._save(fig, f"{value_col}_{agg}_by_{category_col}_bar.png")

    # ------------------------------------------------------------------
    # Time series
    # ------------------------------------------------------------------
    def plot_time_trend(self, date_col: str = "order_date", value_col: str = "revenue", freq: str = "ME"):
        if not self._has_columns(date_col, value_col):
            return None
        if not pd.api.types.is_datetime64_any_dtype(self.df[date_col]):
            logger.warning(f"Skipping time trend - '{date_col}' is not a datetime column.")
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        trend = self.df.set_index(date_col).resample(freq)[value_col].sum()
        trend.plot(ax=ax, marker="o", color="#F18F01")
        ax.set_title(f"{value_col.replace('_', ' ').title()} Trend Over Time")
        ax.set_ylabel(value_col.replace("_", " ").title())
        ax.set_xlabel("Date")
        return self._save(fig, f"{value_col}_trend.png")

    # ------------------------------------------------------------------
    # Orchestration
    # ------------------------------------------------------------------
    def generate_all(self) -> list:
        """
        Generate the full standard set of EDA charts, skipping any chart
        whose required columns aren't present in this dataset.
        """
        logger.info("Generating full visualization suite.")
        candidate_charts = [
            lambda: self.plot_revenue_distribution("revenue"),
            lambda: self.plot_boxplot_by_category("category", "revenue"),
            lambda: self.plot_violin_by_category("category", "revenue"),
            lambda: self.plot_correlation_heatmap(),
            lambda: self.plot_pairplot(),
            lambda: self.plot_scatter("customer_age", "customer_rating", "category"),
            lambda: self.plot_count("region"),
            lambda: self.plot_pie("payment_method"),
            lambda: self.plot_bar_aggregate("category", "revenue", "sum"),
            lambda: self.plot_time_trend("order_date", "revenue"),
        ]
        paths = []
        for chart_fn in tqdm(candidate_charts, desc="Generating charts", unit="chart"):
            try:
                path = chart_fn()
                if path:
                    paths.append(path)
            except Exception:
                logger.exception("Chart generation failed for one chart; continuing with the rest.")
        return paths
