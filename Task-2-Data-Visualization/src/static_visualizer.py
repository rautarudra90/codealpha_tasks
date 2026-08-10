"""
static_visualizer.py
----------------------
Generates a comprehensive suite of static, publication-quality charts using
Matplotlib and Seaborn. Designed to form the core of a data-visualization
portfolio: clear titles, labeled axes, readable color palettes, and
annotations that reveal insights at a glance.
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 120
plt.rcParams["axes.titlesize"] = 14
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11


class StaticVisualizer:
    """Produces a portfolio-quality set of static charts saved as PNG."""

    def __init__(self, df: pd.DataFrame, output_dir: str = "output"):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _save(self, fig, filename: str) -> str:
        path = os.path.join(self.output_dir, filename)
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        logger.info(f"Saved: {path}")
        return path

    def chart_revenue_trend(self) -> str:
        """Line chart: monthly revenue trend with a rolling average overlay."""
        fig, ax = plt.subplots(figsize=(10, 5))
        monthly = self.df.set_index("order_date").resample("ME")["revenue"].sum()
        rolling = monthly.rolling(3, min_periods=1).mean()

        ax.plot(monthly.index, monthly.values, marker="o", label="Monthly Revenue", color="#3E92CC")
        ax.plot(rolling.index, rolling.values, linestyle="--", label="3-Month Rolling Avg", color="#D8315B")
        ax.set_title("Monthly Revenue Trend with Rolling Average")
        ax.set_ylabel("Total Revenue")
        ax.set_xlabel("Month")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        ax.legend()
        return self._save(fig, "01_revenue_trend.png")

    def chart_category_performance(self) -> str:
        """Horizontal bar chart: total revenue by category, ranked."""
        fig, ax = plt.subplots(figsize=(9, 5.5))
        totals = self.df.groupby("category")["revenue"].sum().sort_values()
        bars = ax.barh(totals.index, totals.values, color=sns.color_palette("crest", len(totals)))
        for bar, value in zip(bars, totals.values):
            ax.text(value, bar.get_y() + bar.get_height() / 2, f" ${value:,.0f}",
                    va="center", fontsize=9)
        ax.set_title("Total Revenue by Product Category")
        ax.set_xlabel("Total Revenue")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
        return self._save(fig, "02_category_revenue_ranked.png")

    def chart_region_payment_heatmap(self) -> str:
        """Heatmap: average revenue per region x payment method."""
        fig, ax = plt.subplots(figsize=(9, 5.5))
        pivot = self.df.pivot_table(values="revenue", index="region",
                                     columns="payment_method", aggfunc="mean")
        sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlGnBu", ax=ax, cbar_kws={"label": "Avg Revenue"})
        ax.set_title("Average Revenue: Region vs Payment Method")
        return self._save(fig, "03_region_payment_heatmap.png")

    def chart_discount_impact(self) -> str:
        """Violin plot: revenue distribution by discount bracket."""
        fig, ax = plt.subplots(figsize=(9, 5.5))
        df = self.df.copy()
        df["discount_bracket"] = pd.cut(
            df["discount_pct"], bins=[-1, 0, 10, 20, 100],
            labels=["No Discount", "1-10%", "11-20%", "21%+"]
        )
        sns.violinplot(data=df, x="discount_bracket", y="revenue", ax=ax,
                        hue="discount_bracket", palette="rocket", legend=False, cut=0)
        ax.set_ylim(0, df["revenue"].quantile(0.95))
        ax.set_title("Revenue Distribution by Discount Bracket")
        ax.set_xlabel("Discount Bracket")
        return self._save(fig, "04_discount_impact.png")

    def chart_age_group_spending(self) -> str:
        """Bar chart: average revenue per customer age group."""
        fig, ax = plt.subplots(figsize=(9, 5.5))
        df = self.df.copy()
        df["age_group"] = pd.cut(
            df["customer_age"], bins=[17, 25, 35, 45, 55, 70],
            labels=["18-25", "26-35", "36-45", "46-55", "56-70"]
        )
        avg_rev = df.groupby("age_group", observed=True)["revenue"].mean()
        sns.barplot(x=avg_rev.index, y=avg_rev.values, ax=ax,
                    hue=avg_rev.index, palette="flare", legend=False)
        ax.set_title("Average Order Revenue by Customer Age Group")
        ax.set_ylabel("Average Revenue")
        ax.set_xlabel("Age Group")
        return self._save(fig, "05_age_group_spending.png")

    def chart_rating_distribution(self) -> str:
        """Distribution of customer ratings with mean marker."""
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.histplot(self.df["customer_rating"].dropna(), bins=20, kde=True,
                     ax=ax, color="#5C4B99")
        mean_rating = self.df["customer_rating"].mean()
        ax.axvline(mean_rating, color="#D8315B", linestyle="--",
                    label=f"Mean = {mean_rating:.2f}")
        ax.set_title("Customer Rating Distribution")
        ax.legend()
        return self._save(fig, "06_rating_distribution.png")

    def chart_regional_share_pie(self) -> str:
        """Pie/donut chart: share of total orders per region."""
        fig, ax = plt.subplots(figsize=(7, 7))
        counts = self.df["region"].value_counts()
        colors = sns.color_palette("Set2", len(counts))
        wedges, texts, autotexts = ax.pie(
            counts.values, labels=counts.index, autopct="%1.1f%%",
            startangle=90, colors=colors, pctdistance=0.8,
            wedgeprops=dict(width=0.4)
        )
        ax.set_title("Share of Orders by Region")
        return self._save(fig, "07_regional_share_donut.png")

    def generate_all(self) -> list:
        logger.info("Generating full static visualization suite.")
        return [
            self.chart_revenue_trend(),
            self.chart_category_performance(),
            self.chart_region_payment_heatmap(),
            self.chart_discount_impact(),
            self.chart_age_group_spending(),
            self.chart_rating_distribution(),
            self.chart_regional_share_pie(),
        ]
