"""
main.py
--------
Entry point for the Data Visualization project (static/portfolio mode).

Generates the full suite of static charts and the accompanying data-story
Markdown report. For the interactive dashboard experience, run:
    streamlit run dashboard.py

Usage:
    python main.py
"""

import os
import sys
import traceback

from src.logger_config import get_logger
from src.data_loader import DataLoader, DataLoadError
from src.static_visualizer import StaticVisualizer
from src.story_builder import StoryBuilder

logger = get_logger("main")

DATA_PATH = os.path.join("data", "sample_dataset.csv")
OUTPUT_DIR = "output"


class VisualizationPipeline:
    """Coordinates static chart generation and data-story creation."""

    def __init__(self, data_path: str, output_dir: str):
        self.data_path = data_path
        self.output_dir = output_dir

    def run(self):
        logger.info("=" * 70)
        logger.info("Starting Data Visualization Pipeline")
        logger.info("=" * 70)

        df = self._load_data()

        visualizer = StaticVisualizer(df, output_dir=self.output_dir)
        chart_paths = visualizer.generate_all()

        story = StoryBuilder(df, output_dir=self.output_dir)
        story_path = story.build(chart_paths)

        logger.info("Data Visualization Pipeline completed successfully.")
        return chart_paths, story_path

    def _load_data(self):
        try:
            loader = DataLoader(self.data_path)
            return loader.load(clean=True)
        except DataLoadError as e:
            logger.error(f"Data loading failed: {e}")
            print(f"\n[ERROR] Could not load dataset: {e}")
            print("Attempting to auto-generate the sample dataset...")
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
            import generate_dataset  # noqa
            generate_dataset.main()
            loader = DataLoader(self.data_path)
            return loader.load(clean=True)


def main():
    try:
        pipeline = VisualizationPipeline(DATA_PATH, OUTPUT_DIR)
        chart_paths, story_path = pipeline.run()
        print("\n✅ Visualization pipeline completed successfully.")
        print(f"🖼️  Charts ({len(chart_paths)}): {OUTPUT_DIR}/*.png")
        print(f"📄 Data story: {story_path}")
        print("📝 Logs: logs/visualization_project.log")
        print("\n💡 Tip: run 'streamlit run dashboard.py' for the interactive dashboard.")
    except Exception as e:
        logger.error(f"Fatal error in pipeline: {e}")
        logger.debug(traceback.format_exc())
        print(f"\n[FATAL ERROR] The pipeline failed: {e}")
        print("See logs/visualization_project.log for full details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
