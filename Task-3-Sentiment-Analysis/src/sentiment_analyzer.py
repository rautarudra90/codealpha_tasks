"""
sentiment_analyzer.py
------------------------
Performs sentiment classification (positive / negative / neutral) using an
ensemble of two well-established lexicon-based NLP tools:

    1. VADER (Valence Aware Dictionary and sEntiment Reasoner) - tuned for
       social-media-style text (handles emojis, punctuation emphasis, slang).
    2. TextBlob's pattern-based polarity analyzer - a general-purpose
       lexicon/rule-based sentiment scorer.

Combining both reduces the risk of any single lexicon's blind spots and
produces a more robust final label.
"""

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
from src.logger_config import get_logger

logger = get_logger(__name__)


class SentimentAnalyzer:
    """Classifies text sentiment using a VADER + TextBlob ensemble."""

    def __init__(self, neutral_threshold: float = 0.05):
        """
        Args:
            neutral_threshold (float): Compound/polarity score band around
                zero that is classified as 'neutral'.
        """
        self.vader = SentimentIntensityAnalyzer()
        self.neutral_threshold = neutral_threshold

    def analyze_text(self, text: str) -> dict:
        """
        Analyze a single piece of text.

        Args:
            text (str): Cleaned text to analyze.

        Returns:
            dict: vader_compound, textblob_polarity, textblob_subjectivity,
            ensemble_score, and final sentiment label.
        """
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores["compound"]

        blob = TextBlob(text)
        tb_polarity = blob.sentiment.polarity
        tb_subjectivity = blob.sentiment.subjectivity

        # Simple weighted ensemble: VADER is tuned for informal/social text,
        # so it gets slightly more weight than TextBlob's general-purpose score.
        ensemble_score = (0.6 * vader_compound) + (0.4 * tb_polarity)

        if ensemble_score >= self.neutral_threshold:
            label = "positive"
        elif ensemble_score <= -self.neutral_threshold:
            label = "negative"
        else:
            label = "neutral"

        return {
            "vader_compound": round(vader_compound, 4),
            "textblob_polarity": round(tb_polarity, 4),
            "textblob_subjectivity": round(tb_subjectivity, 4),
            "ensemble_score": round(ensemble_score, 4),
            "predicted_sentiment": label,
        }

    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = "clean_text") -> pd.DataFrame:
        """
        Apply sentiment analysis to every row of a DataFrame.

        Args:
            df (pd.DataFrame): Dataset with a cleaned text column.
            text_column (str): Column containing text to analyze.

        Returns:
            pd.DataFrame: Original dataset with sentiment columns appended.
        """
        logger.info(f"Running sentiment analysis on {len(df)} records.")
        results = df[text_column].apply(self.analyze_text).apply(pd.Series)
        output = pd.concat([df.reset_index(drop=True), results.reset_index(drop=True)], axis=1)
        logger.info("Sentiment analysis complete.")
        return output

    def evaluate_accuracy(self, df: pd.DataFrame, true_col: str = "true_sentiment",
                           pred_col: str = "predicted_sentiment") -> dict:
        """
        If ground-truth labels are available, compute accuracy metrics.

        Args:
            df (pd.DataFrame): Dataset containing both true and predicted labels.
            true_col (str): Column with ground-truth sentiment.
            pred_col (str): Column with predicted sentiment.

        Returns:
            dict: Overall accuracy and per-class precision/recall/f1 (macro).
        """
        if true_col not in df.columns:
            logger.info("No ground-truth column found; skipping accuracy evaluation.")
            return {}

        from sklearn.metrics import accuracy_score, classification_report

        logger.info("Evaluating prediction accuracy against ground-truth labels.")
        accuracy = accuracy_score(df[true_col], df[pred_col])
        report = classification_report(df[true_col], df[pred_col], output_dict=True, zero_division=0)

        logger.info(f"Overall accuracy: {accuracy:.4f}")
        return {
            "accuracy": round(accuracy, 4),
            "classification_report": report,
        }
