"""
preprocessor.py
-----------------
Cleans and normalizes raw text before sentiment/emotion analysis:
lowercasing, URL/mention/hashtag stripping, punctuation handling,
whitespace normalization, and empty-text filtering.
"""

import re
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)

URL_PATTERN = re.compile(r"http\S+|www\.\S+")
MENTION_PATTERN = re.compile(r"@\w+")
HASHTAG_PATTERN = re.compile(r"#(\w+)")
NON_ALPHA_PATTERN = re.compile(r"[^a-zA-Z0-9\s!?.,':)(-]")
MULTI_SPACE_PATTERN = re.compile(r"\s+")


class TextPreprocessor:
    """Cleans raw text data for downstream NLP analysis."""

    def clean_text(self, text: str) -> str:
        """
        Clean a single text string.

        Args:
            text (str): Raw input text.

        Returns:
            str: Cleaned text (empty string if input was invalid).
        """
        if not isinstance(text, str) or not text.strip():
            return ""

        cleaned = text.strip()
        cleaned = URL_PATTERN.sub("", cleaned)
        cleaned = MENTION_PATTERN.sub("", cleaned)
        cleaned = HASHTAG_PATTERN.sub(r"\1", cleaned)
        cleaned = NON_ALPHA_PATTERN.sub("", cleaned)
        cleaned = MULTI_SPACE_PATTERN.sub(" ", cleaned).strip()
        return cleaned

    def process_dataframe(self, df: pd.DataFrame, text_column: str = "text") -> pd.DataFrame:
        """
        Apply cleaning to an entire DataFrame column and drop rows that
        become empty after cleaning.

        Args:
            df (pd.DataFrame): Input dataset.
            text_column (str): Name of the column containing raw text.

        Returns:
            pd.DataFrame: Dataset with an added 'clean_text' column,
            with empty/invalid rows removed.
        """
        logger.info(f"Preprocessing {len(df)} text records.")
        df = df.copy()
        df["clean_text"] = df[text_column].apply(self.clean_text)

        before = len(df)
        df = df[df["clean_text"].str.len() > 0].reset_index(drop=True)
        after = len(df)

        removed = before - after
        if removed > 0:
            logger.info(f"Removed {removed} empty/invalid rows after cleaning.")

        # Also drop exact duplicate cleaned texts to avoid skewing aggregate stats.
        before_dedupe = len(df)
        df = df.drop_duplicates(subset="clean_text").reset_index(drop=True)
        deduped = before_dedupe - len(df)
        if deduped > 0:
            logger.info(f"Removed {deduped} duplicate rows after cleaning.")

        logger.info(f"Preprocessing complete: {len(df)} usable records remain.")
        return df
