"""
report_generator.py
----------------------
Compiles sentiment and emotion analysis findings into a single, decision-
oriented Markdown report — including overall sentiment mix, accuracy
metrics (when ground truth is available), dominant emotions, and
actionable business recommendations.
"""

import os
from datetime import datetime
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Builds a consolidated Markdown sentiment analysis report."""

    def __init__(self, output_dir: str = "output"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def build(self, df: pd.DataFrame, accuracy_info: dict, chart_paths: list) -> str:
        lines = []
        lines.append("# Sentiment Analysis Report\n")
        lines.append(f"_Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_\n")

        lines.append("\n## 1. Overview\n")
        lines.append(
            f"- Total texts analyzed: **{len(df)}**\n"
            f"- Sources covered: **{', '.join(sorted(df['source'].dropna().unique()))}**\n"
        )

        sentiment_counts = df["predicted_sentiment"].value_counts()
        sentiment_pct = (sentiment_counts / len(df) * 100).round(1)
        lines.append("\n## 2. Overall Sentiment Breakdown\n")
        lines.append("| Sentiment | Count | Percentage |\n|---|---|---|\n")
        for sentiment in ["positive", "neutral", "negative"]:
            count = int(sentiment_counts.get(sentiment, 0))
            pct = sentiment_pct.get(sentiment, 0.0)
            lines.append(f"| {sentiment.capitalize()} | {count} | {pct}% |\n")

        if accuracy_info:
            lines.append("\n## 3. Model Accuracy vs Ground Truth\n")
            lines.append(f"- Overall accuracy: **{accuracy_info['accuracy'] * 100:.2f}%**\n")
            report = accuracy_info["classification_report"]
            lines.append("\n| Class | Precision | Recall | F1-score | Support |\n|---|---|---|---|---|\n")
            for label in ["positive", "neutral", "negative"]:
                if label in report:
                    r = report[label]
                    lines.append(
                        f"| {label.capitalize()} | {r['precision']:.2f} | {r['recall']:.2f} | "
                        f"{r['f1-score']:.2f} | {int(r['support'])} |\n"
                    )

        emotion_cols = ["joy", "anger", "sadness", "fear", "trust", "surprise"]
        emotion_totals = df[emotion_cols].sum().sort_values(ascending=False)
        lines.append("\n## 4. Dominant Emotions Detected\n")
        lines.append("| Emotion | Total Word Matches |\n|---|---|\n")
        for emotion, total in emotion_totals.items():
            lines.append(f"| {emotion.capitalize()} | {int(total)} |\n")

        lines.append("\n## 5. Sentiment by Source\n")
        source_sentiment = pd.crosstab(df["source"], df["predicted_sentiment"], normalize="index") * 100
        lines.append(source_sentiment.round(1).to_markdown())
        lines.append("\n")

        lines.append("\n## 6. Visualizations\n")
        for path in chart_paths:
            filename = os.path.basename(path)
            lines.append(f"![{filename}]({filename})\n")

        top_negative_item = None
        if "item" in df.columns:
            negative_by_item = df[df["predicted_sentiment"] == "negative"]["item"].value_counts()
            if not negative_by_item.empty:
                top_negative_item = negative_by_item.idxmax()

        lines.append("\n## 7. Business Insights & Recommendations\n")
        insights = [
            f"- Positive sentiment accounts for **{sentiment_pct.get('positive', 0)}%** of all "
            "analyzed text, indicating overall favorable public perception.",
            f"- Negative sentiment accounts for **{sentiment_pct.get('negative', 0)}%**; the "
            "top negative keywords chart highlights recurring pain points worth investigating.",
            f"- The dominant emotion detected overall is **{emotion_totals.index[0]}**, which "
            "should inform tone and messaging in marketing and support communications.",
        ]
        if top_negative_item:
            insights.append(
                f"- **{top_negative_item}** received the most negative mentions and may warrant "
                "a quality or service review."
            )
        lines.append("\n".join(insights))

        path = os.path.join(self.output_dir, "sentiment_report.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        logger.info(f"Sentiment report saved to {path}")
        return path
