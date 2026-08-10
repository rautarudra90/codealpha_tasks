"""
story_builder.py
------------------
Turns raw chart outputs into a compelling written data story: a Markdown
narrative that ties every visualization to a business insight and a
recommended action, designed to support real decision-making.
"""

import os
from datetime import datetime
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)


class StoryBuilder:
    """Builds a narrative Markdown report linking charts to insights."""

    def __init__(self, df: pd.DataFrame, output_dir: str = "output"):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _compute_insights(self) -> dict:
        df = self.df
        top_category = df.groupby("category")["revenue"].sum().idxmax()
        top_region = df["region"].value_counts().idxmax()
        avg_rating = df["customer_rating"].mean()
        discount_corr = df[["discount_pct", "revenue"]].corr().iloc[0, 1]
        best_month = df.set_index("order_date").resample("ME")["revenue"].sum().idxmax()
        avg_delivery = df[df["delivery_days"] > 0]["delivery_days"].mean()

        return {
            "top_category": top_category,
            "top_region": top_region,
            "avg_rating": round(avg_rating, 2),
            "discount_corr": round(discount_corr, 3),
            "best_month": best_month.strftime("%B %Y"),
            "avg_delivery": round(avg_delivery, 1),
        }

    def build(self, chart_paths: list) -> str:
        insights = self._compute_insights()
        chart_names = [os.path.basename(p) for p in chart_paths]

        lines = []
        lines.append("# Data Story: E-Commerce Sales Performance\n")
        lines.append(f"_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")

        lines.append("\n## Executive Summary\n")
        lines.append(
            f"Across the analyzed period, **{insights['top_category']}** emerged as the "
            f"top-performing category by total revenue, while **{insights['top_region']}** "
            f"generated the highest order volume. The strongest revenue month was "
            f"**{insights['best_month']}**. Average customer satisfaction sits at "
            f"**{insights['avg_rating']} / 5**, and average delivery time is "
            f"**{insights['avg_delivery']} days**.\n"
        )

        lines.append("\n## Chart 1 — Revenue Trend\n")
        lines.append(f"![chart]({chart_names[0]})\n")
        lines.append(
            "The rolling average smooths out month-to-month noise and makes the underlying "
            "growth trajectory visible, which is more decision-useful than raw monthly totals "
            "alone.\n"
        )

        lines.append("\n## Chart 2 — Category Performance\n")
        lines.append(f"![chart]({chart_names[1]})\n")
        lines.append(
            f"**{insights['top_category']}** leads total revenue. Category ranking should "
            "directly inform inventory investment and promotional budget allocation.\n"
        )

        lines.append("\n## Chart 3 — Region vs Payment Method\n")
        lines.append(f"![chart]({chart_names[2]})\n")
        lines.append(
            "This heatmap surfaces regional payment preferences — useful for prioritizing "
            "which payment gateways to optimize per region.\n"
        )

        lines.append("\n## Chart 4 — Discount Impact\n")
        lines.append(f"![chart]({chart_names[3]})\n")
        corr_direction = "positively" if insights["discount_corr"] > 0 else "negatively"
        lines.append(
            f"Discount percentage is {corr_direction} correlated with revenue "
            f"(r = {insights['discount_corr']}). This should be weighed against margin impact "
            "before scaling promotions further.\n"
        )

        lines.append("\n## Chart 5 — Age Group Spending\n")
        lines.append(f"![chart]({chart_names[4]})\n")
        lines.append(
            "Spending varies meaningfully by age bracket, suggesting an opportunity for "
            "age-targeted marketing campaigns.\n"
        )

        lines.append("\n## Chart 6 — Rating Distribution\n")
        lines.append(f"![chart]({chart_names[5]})\n")
        lines.append(
            f"The average rating of {insights['avg_rating']} / 5 indicates generally positive "
            "sentiment, with a distribution worth monitoring for any leftward (lower-rating) "
            "shift over time.\n"
        )

        lines.append("\n## Chart 7 — Regional Order Share\n")
        lines.append(f"![chart]({chart_names[6]})\n")
        lines.append(
            f"**{insights['top_region']}** contributes the largest share of order volume, "
            "which should factor into logistics and warehouse placement decisions.\n"
        )

        lines.append("\n## Recommended Actions\n")
        lines.append(
            f"1. Double down on **{insights['top_category']}** with expanded inventory and "
            "featured placement.\n"
            f"2. Investigate why **{insights['best_month']}** outperformed — replicate the "
            "conditions (campaigns, seasonality) if possible.\n"
            "3. Reassess discount strategy in light of its measured relationship with revenue.\n"
            f"4. Prioritize logistics investment in **{insights['top_region']}** given its "
            "order volume share.\n"
        )

        path = os.path.join(self.output_dir, "data_story.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info(f"Data story saved to {path}")
        return path
