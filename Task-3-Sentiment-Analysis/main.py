"""
main.py
--------
Entry point for the Sentiment Analysis project.

This script orchestrates the full sentiment analysis pipeline:
    1. Load the raw text dataset (Amazon-style reviews / social posts / news).
    2. Clean and normalize the text.
    3. Classify sentiment (positive / negative / neutral) using a VADER +
       TextBlob ensemble.
    4. Detect discrete emotions (joy, anger, sadness, fear, trust, surprise)
       using an embedded lexicon.
    5. Evaluate prediction accuracy against ground-truth labels (if present).
    6. Generate visualizations.
    7. Compile everything into a single Markdown report.
    8. Save the fully processed dataset to output/processed_results.csv.

Usage:
    python main.py
"""

import os
import sys
import traceback

from src.logger_config import get_logger
from src.data_loader import DataLoader, DataLoadError
from src.preprocessor import TextPreprocessor
from src.sentiment_analyzer import SentimentAnalyzer
from src.emotion_detector import EmotionDetector
from src.visualizer import SentimentVisualizer
from src.report_generator import ReportGenerator

logger = get_logger("main")

DATA_PATH = os.path.join("data", "sample_reviews.csv")
OUTPUT_DIR = "output"


class SentimentPipeline:
    """Coordinates the full sentiment + emotion analysis workflow."""

    def __init__(self, data_path: str, output_dir: str):
        self.data_path = data_path
        self.output_dir = output_dir

    def run(self):
        logger.info("=" * 70)
        logger.info("Starting Sentiment Analysis Pipeline")
        logger.info("=" * 70)

        raw_df = self._load_data()

        preprocessor = TextPreprocessor()
        clean_df = preprocessor.process_dataframe(raw_df, text_column="text")

        analyzer = SentimentAnalyzer()
        sentiment_df = analyzer.analyze_dataframe(clean_df, text_column="clean_text")

        emotion_detector = EmotionDetector()
        full_df = emotion_detector.analyze_dataframe(sentiment_df, text_column="clean_text")

        accuracy_info = analyzer.evaluate_accuracy(full_df)

        visualizer = SentimentVisualizer(full_df, output_dir=self.output_dir)
        chart_paths = visualizer.generate_all()

        report_generator = ReportGenerator(output_dir=self.output_dir)
        report_path = report_generator.build(full_df, accuracy_info, chart_paths)

        results_path = os.path.join(self.output_dir, "processed_results.csv")
        full_df.to_csv(results_path, index=False)
        logger.info(f"Processed results saved to {results_path}")

        logger.info("Sentiment Analysis Pipeline completed successfully.")
        return full_df, accuracy_info, chart_paths, report_path, results_path

    def _load_data(self):
        try:
            loader = DataLoader(self.data_path)
            return loader.load()
        except DataLoadError as e:
            logger.error(f"Data loading failed: {e}")
            print(f"\n[ERROR] Could not load dataset: {e}")
            print("Attempting to auto-generate the sample dataset...")
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
            import generate_dataset  # noqa
            generate_dataset.main()
            loader = DataLoader(self.data_path)
            return loader.load()


def main():
    try:
        pipeline = SentimentPipeline(DATA_PATH, OUTPUT_DIR)
        full_df, accuracy_info, chart_paths, report_path, results_path = pipeline.run()

        print("\n✅ Sentiment analysis pipeline completed successfully.")
        print(f"📊 Records analyzed: {len(full_df)}")
        if accuracy_info:
            print(f"🎯 Accuracy vs ground truth: {accuracy_info['accuracy'] * 100:.2f}%")
        print(f"📄 Report: {report_path}")
        print(f"🖼️  Charts ({len(chart_paths)}): {OUTPUT_DIR}/*.png")
        print(f"💾 Full results CSV: {results_path}")
        print("📝 Logs: logs/sentiment_project.log")
    except Exception as e:
        logger.error(f"Fatal error in pipeline: {e}")
        logger.debug(traceback.format_exc())
        print(f"\n[FATAL ERROR] The pipeline failed: {e}")
        print("See logs/sentiment_project.log for full details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
