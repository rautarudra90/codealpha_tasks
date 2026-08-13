"""
emotion_detector.py
----------------------
Detects specific emotions (joy, anger, sadness, fear, trust, surprise)
within text using a curated, embedded lexicon-based approach inspired by
the NRC Emotion Lexicon methodology. No external downloads are required —
the lexicon is embedded directly in this module so the project works
fully offline.
"""

import re
from collections import Counter
import pandas as pd
from src.logger_config import get_logger

logger = get_logger(__name__)

# A compact, hand-curated emotion lexicon. Each emotion maps to a set of
# representative trigger words/stems. This is intentionally lightweight
# (suitable for a portfolio project) rather than an exhaustive dictionary.
EMOTION_LEXICON = {
    "joy": {
        "happy", "love", "great", "wonderful", "excellent", "amazing", "fantastic",
        "delight", "delighted", "glad", "pleased", "enjoy", "enjoyed", "awesome",
        "excited", "impressive", "impressed", "outstanding", "perfect", "best",
    },
    "anger": {
        "angry", "hate", "furious", "annoyed", "frustrated", "frustrating", "outraged",
        "mad", "rage", "irritated", "unacceptable", "disgusted", "resent", "hostile",
    },
    "sadness": {
        "sad", "disappointed", "disappointing", "regret", "unhappy", "upset",
        "heartbroken", "miserable", "sorrow", "depressed", "gloomy", "let", "down",
    },
    "fear": {
        "afraid", "scared", "worried", "anxious", "nervous", "concerned", "fear",
        "terrified", "panic", "risk", "risky", "uncertain", "unsafe",
    },
    "trust": {
        "reliable", "trust", "trustworthy", "dependable", "honest", "confident",
        "secure", "safe", "recommend", "recommended", "consistent", "loyal",
    },
    "surprise": {
        "surprised", "surprising", "unexpected", "shocked", "shocking", "wow",
        "unbelievable", "astonished", "sudden", "suddenly",
    },
}

WORD_PATTERN = re.compile(r"[a-zA-Z']+")


class EmotionDetector:
    """Detects and scores discrete emotions present in text using a lexicon."""

    def __init__(self, lexicon: dict = None):
        self.lexicon = lexicon or EMOTION_LEXICON
        # Build a reverse lookup: word -> set of emotions, for fast scoring.
        self._word_to_emotions = {}
        for emotion, words in self.lexicon.items():
            for w in words:
                self._word_to_emotions.setdefault(w, set()).add(emotion)

    def detect_emotions(self, text: str) -> dict:
        """
        Detect emotion word counts within a single text.

        Args:
            text (str): Cleaned text to analyze.

        Returns:
            dict: Count of matched words per emotion category, plus the
            single dominant emotion (or 'none' if no matches).
        """
        tokens = [t.lower() for t in WORD_PATTERN.findall(text)]
        counts = Counter({emotion: 0 for emotion in self.lexicon})

        for token in tokens:
            emotions = self._word_to_emotions.get(token)
            if emotions:
                for e in emotions:
                    counts[e] += 1

        total_matches = sum(counts.values())
        dominant = max(counts, key=counts.get) if total_matches > 0 else "none"

        result = dict(counts)
        result["dominant_emotion"] = dominant
        result["total_emotion_words"] = total_matches
        return result

    def analyze_dataframe(self, df: pd.DataFrame, text_column: str = "clean_text") -> pd.DataFrame:
        """
        Apply emotion detection across an entire DataFrame.

        Args:
            df (pd.DataFrame): Dataset with a cleaned text column.
            text_column (str): Column containing text to analyze.

        Returns:
            pd.DataFrame: Original dataset with emotion columns appended.
        """
        logger.info(f"Running emotion detection on {len(df)} records.")
        results = df[text_column].apply(self.detect_emotions).apply(pd.Series)
        output = pd.concat([df.reset_index(drop=True), results.reset_index(drop=True)], axis=1)
        logger.info("Emotion detection complete.")
        return output
