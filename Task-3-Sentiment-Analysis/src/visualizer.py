"""
visualizer.py
--------------
Generates visualizations of sentiment and emotion analysis results:
sentiment distribution, sentiment by source, emotion breakdown, sentiment
trend over time, and a word-frequency chart for negative feedback (useful
for identifying recurring pain points).
"""

import os
from collections import Counter
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.logger_config import get_logger
from src.emotion_detector import WORD_PATTERN

logger = get_logger(__name__)
sns.set_theme(style="whitegrid")

SENTIMENT_COLORS = {"positive": "#2E8B57", "neutral": "#B8B8B8", "negative": "#D62839"}
SENTIMENT_ORDER = ["positive", "neutral", "negative"]

STOPWORDS = {
    "the", "a", "an", "is", "it", "i", "to", "and", "of", "this", "my", "for",
    "in", "on", "with", "was", "are", "so", "very", "just", "have", "has",
    "be", "as", "at", "but", "not", "you", "your", "all", "after", "still",
    "will", "am", "me", "that", "its", "im",
}


class SentimentVisualizer:
    """Creates and saves sentiment/emotion analysis charts."""

    def __init__(self, df: pd.DataFrame, output_dir: str = "output"):
        self.df = df
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def _save(self, fig, filename: str) -> str:
        path = os.path.join(self.output_dir, filename)
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight", dpi=150)
        plt.close(fig)
        logger.info(f"Saved chart: {path}")
        return path

    def plot_sentiment_distribution(self) -> str:
        fig, ax = plt.subplots(figsize=(7, 5))
        counts = self.df["predicted_sentiment"].value_counts().reindex(SENTIMENT_ORDER).fillna(0)
        colors = [SENTIMENT_COLORS[s] for s in SENTIMENT_ORDER]
        bars = ax.bar(counts.index, counts.values, color=colors)
        for bar, val in zip(bars, counts.values):
            ax.text(bar.get_x() + bar.get_width() / 2, val, f"{int(val)}",
                    ha="center", va="bottom", fontsize=10)
        ax.set_title("Overall Sentiment Distribution")
        ax.set_ylabel("Number of Texts")
        return self._save(fig, "sentiment_distribution.png")

    def plot_sentiment_by_source(self) -> str:
        fig, ax = plt.subplots(figsize=(10, 5.5))
        pivot = pd.crosstab(self.df["source"], self.df["predicted_sentiment"], normalize="index") * 100
        pivot = pivot.reindex(columns=SENTIMENT_ORDER, fill_value=0)
        pivot.plot(kind="bar", stacked=True, ax=ax,
                   color=[SENTIMENT_COLORS[s] for s in SENTIMENT_ORDER])
        ax.set_title("Sentiment Composition by Source (%)")
        ax.set_ylabel("Percentage of Texts")
        ax.set_xlabel("Source")
        ax.legend(title="Sentiment", bbox_to_anchor=(1.02, 1), loc="upper left")
        plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
        return self._save(fig, "sentiment_by_source.png")

    def plot_emotion_breakdown(self) -> str:
        fig, ax = plt.subplots(figsize=(9, 5.5))
        emotion_cols = ["joy", "anger", "sadness", "fear", "trust", "surprise"]
        totals = self.df[emotion_cols].sum().sort_values(ascending=False)
        sns.barplot(x=totals.index, y=totals.values, ax=ax,
                    hue=totals.index, palette="rocket", legend=False)
        ax.set_title("Total Emotion Word Matches Across All Texts")
        ax.set_ylabel("Word Match Count")
        return self._save(fig, "emotion_breakdown.png")

    def plot_sentiment_trend(self) -> str:
        fig, ax = plt.subplots(figsize=(10, 5))
        df = self.df.copy()
        df["month"] = pd.to_datetime(df["review_date"]).dt.to_period("M").dt.to_timestamp()
        trend = pd.crosstab(df["month"], df["predicted_sentiment"]).reindex(
            columns=SENTIMENT_ORDER, fill_value=0
        )
        for sentiment in SENTIMENT_ORDER:
            ax.plot(trend.index, trend[sentiment], marker="o",
                    label=sentiment, color=SENTIMENT_COLORS[sentiment])
        ax.set_title("Sentiment Trend Over Time")
        ax.set_ylabel("Number of Texts")
        ax.set_xlabel("Month")
        ax.legend()
        return self._save(fig, "sentiment_trend.png")

    def plot_negative_keyword_frequency(self, top_n: int = 15) -> str:
        fig, ax = plt.subplots(figsize=(9, 6))
        negative_texts = self.df[self.df["predicted_sentiment"] == "negative"]["clean_text"]
        word_counter = Counter()
        for text in negative_texts:
            words = [w.lower() for w in WORD_PATTERN.findall(text) if w.lower() not in STOPWORDS and len(w) > 2]
            word_counter.update(words)

        top_words = word_counter.most_common(top_n)
        if not top_words:
            ax.text(0.5, 0.5, "No negative texts found", ha="center", va="center")
        else:
            words, counts = zip(*top_words)
            sns.barplot(x=list(counts), y=list(words), ax=ax,
                        hue=list(words), palette="Reds_r", legend=False)
        ax.set_title(f"Top {top_n} Words in Negative Feedback")
        ax.set_xlabel("Frequency")
        return self._save(fig, "negative_keyword_frequency.png")

    def generate_all(self) -> list:
        logger.info("Generating full sentiment visualization suite.")
        return [
            self.plot_sentiment_distribution(),
            self.plot_sentiment_by_source(),
            self.plot_emotion_breakdown(),
            self.plot_sentiment_trend(),
            self.plot_negative_keyword_frequency(),
        ]
