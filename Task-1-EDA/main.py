"""
main.py
--------
Entry point for the Exploratory Data Analysis (EDA) project.

This script orchestrates the full EDA pipeline:
    1. Load the dataset (CSV/Excel/JSON).
    2. Clean it (duplicates, missing values, dtypes, dates, outliers).
    3. Explore its structure (dtypes, shape, missing values, duplicates).
    4. Detect statistical and logical anomalies (IQR, Z-score, Isolation Forest).
    5. Test formal hypotheses using statistics.
    6. Generate visualizations.
    7. Generate plain-English insights.
    8. Compile everything into Markdown / PDF / Excel / CSV reports.

CLI usage:
    python main.py                        # run everything with defaults
    python main.py --dataset file.csv      # use a specific dataset
    python main.py --charts                # charts only (no reports)
    python main.py --report                # reports only (no charts)
    python main.py --all                   # explicit: run everything
    python main.py --skip-clean            # analyze raw data, skip cleaning
    python main.py --no-pdf --no-excel     # limit report formats generated
"""

import argparse
import os
import sys
import time
import traceback

import config
from src.logger_config import get_logger, log_execution_time
from src.data_loader import DataLoader, DataLoadError
from src.data_cleaner import DataCleaner
from src.data_explorer import DataExplorer
from src.anomaly_detector import AnomalyDetector
from src.hypothesis_tester import HypothesisTester
from src.visualizer import EDAVisualizer
from src.insights_generator import InsightsGenerator
from src.report_generator import ReportGenerator

logger = get_logger("main")


class EDAPipeline:
    """Coordinates the full exploratory data analysis workflow."""

    def __init__(self, data_path: str, charts_dir: str, reports_dir: str, args: argparse.Namespace):
        self.data_path = data_path
        self.charts_dir = charts_dir
        self.reports_dir = reports_dir
        self.args = args
        self.df = None

    def run(self):
        start_time = time.perf_counter()
        logger.info("=" * 70)
        logger.info("Starting EDA Pipeline")
        logger.info("=" * 70)

        with log_execution_time(logger, "Data loading"):
            self.df = self._load_data()

        if not self.args.skip_clean:
            with log_execution_time(logger, "Data cleaning"):
                self.df = self._clean_data()

        explorer = DataExplorer(self.df)
        with log_execution_time(logger, "Exploratory analysis"):
            overview = explorer.structural_overview()
            missing_report = explorer.missing_value_report()
            duplicate_report = explorer.duplicate_report()
            numeric_summary = explorer.numeric_summary()
            categorical_summary = explorer.categorical_summary()
            correlation = explorer.correlation_matrix()

        with log_execution_time(logger, "Anomaly detection"):
            anomaly_detector = AnomalyDetector(self.df)
            numeric_cols = [c for c in config.DEFAULT_NUMERIC_COLUMNS if c in self.df.columns]
            outlier_summary = anomaly_detector.summary(numeric_columns=numeric_cols)
            method_comparison = anomaly_detector.compare_methods(numeric_columns=numeric_cols)
            logical_anomalies = anomaly_detector.logical_anomalies()

        with log_execution_time(logger, "Hypothesis testing"):
            tester = HypothesisTester(self.df, alpha=config.HYPOTHESIS_ALPHA)
            hypothesis_results = tester.run_all()

        image_paths = []
        if self.args.charts:
            with log_execution_time(logger, "Chart generation"):
                visualizer = EDAVisualizer(self.df, output_dir=self.charts_dir)
                image_paths = visualizer.generate_all()

        with log_execution_time(logger, "Insight generation"):
            insights = self._generate_insights(correlation, outlier_summary, missing_report, duplicate_report)

        if self.args.report:
            with log_execution_time(logger, "Report generation"):
                self._build_report(
                    overview, missing_report, duplicate_report, numeric_summary,
                    categorical_summary, correlation, outlier_summary, method_comparison,
                    logical_anomalies, hypothesis_results, insights, image_paths,
                )

        elapsed = time.perf_counter() - start_time
        logger.info(f"EDA Pipeline completed successfully in {elapsed:.2f}s.")
        logger.info(f"Charts saved in: {os.path.abspath(self.charts_dir)}")
        logger.info(f"Reports saved in: {os.path.abspath(self.reports_dir)}")

    # ------------------------------------------------------------------
    def _load_data(self):
        try:
            loader = DataLoader(self.data_path)
            return loader.load()
        except DataLoadError as e:
            logger.error(f"Data loading failed: {e}")
            print(f"\n[ERROR] Could not load dataset: {e}")
            if self.data_path == config.DEFAULT_DATASET_PATH:
                print("Attempting to auto-generate the sample dataset...")
                self._auto_generate_dataset()
                loader = DataLoader(self.data_path)
                return loader.load()
            raise

    def _auto_generate_dataset(self):
        """Fallback: regenerate the bundled sample dataset if it is missing."""
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "data"))
        import generate_dataset  # noqa
        generate_dataset.main()

    def _clean_data(self):
        cleaner = DataCleaner(self.df)
        cleaner.run_full_cleaning()
        self.cleaning_report = cleaner.get_report()
        cleaned_df = cleaner.get_cleaned_data()
        os.makedirs(os.path.dirname(config.CLEANED_DATASET_PATH), exist_ok=True)
        cleaned_df.to_csv(config.CLEANED_DATASET_PATH, index=False)
        logger.info(f"Cleaned dataset saved to {config.CLEANED_DATASET_PATH}")
        return cleaned_df

    def _generate_insights(self, correlation, outlier_summary, missing_report, duplicate_report):
        generator = InsightsGenerator(self.df)
        generator.data_quality_summary(missing_report, duplicate_report)
        generator.correlation_highlights(correlation)
        generator.outlier_summary(outlier_summary)
        if {"category", "revenue"}.issubset(self.df.columns):
            generator.category_performance("category", "revenue")
        if {"order_date", "revenue"}.issubset(self.df.columns):
            generator.trend_analysis("order_date", "revenue")
        return generator

    def _build_report(self, overview, missing_report, duplicate_report,
                       numeric_summary, categorical_summary, correlation,
                       outlier_summary, method_comparison, logical_anomalies,
                       hypothesis_results, insights: InsightsGenerator, image_paths):
        report = ReportGenerator(output_dir=self.reports_dir)
        report.add_title(f"{config.REPORT_TITLE} — {os.path.basename(self.data_path)}")

        report.add_section(
            "Executive Summary",
            f"This report covers a dataset of **{overview['n_rows']:,} rows** and "
            f"**{overview['n_columns']} columns**. "
            f"{duplicate_report['duplicate_rows']} duplicate row(s) and "
            f"{int(missing_report['missing_count'].sum()) if not missing_report.empty else 0} "
            f"missing value(s) were found during exploration. "
            f"{len(hypothesis_results)} hypothesis test(s) were run."
        )

        report.add_dict_as_table("Dataset Information", {
            "Rows": overview["n_rows"],
            "Columns": overview["n_columns"],
            "Memory Usage (MB)": overview["memory_usage_mb"],
        })

        if hasattr(self, "cleaning_report"):
            cr = self.cleaning_report
            report.add_dict_as_table("Cleaning Summary", {
                "Original Shape": str(cr.get("original_shape")),
                "Final Shape": str(cr.get("final_shape")),
                "Duplicates Removed": cr.get("duplicates_removed", 0),
                "Columns Renamed": len(cr.get("columns_renamed", {})),
                "Dtype Fixes": len(cr.get("dtype_fixes", {})),
                "Dates Converted": ", ".join(cr.get("dates_converted", [])) or "None",
                "Columns With Outliers Capped": len(cr.get("outliers_capped", {})),
            })

        if not missing_report.empty:
            report.add_dataframe("Missing Values Report", missing_report)
        else:
            report.add_section("Missing Values Report", "No missing values detected.")

        report.add_dataframe("Numeric Summary Statistics", numeric_summary.round(2))
        report.add_dataframe("Correlation Matrix", correlation.round(2))
        report.add_dataframe("Outlier Summary (IQR Method)", outlier_summary)
        report.add_dataframe("Anomaly Detection Method Comparison", method_comparison)

        if logical_anomalies:
            anomaly_text = "\n".join(
                f"- **{key}**: {len(frame)} rows flagged" for key, frame in logical_anomalies.items()
            )
            report.add_section("Logical / Domain-Rule Anomalies", anomaly_text)
        else:
            report.add_section("Logical / Domain-Rule Anomalies", "None detected.")

        if hypothesis_results:
            report.add_hypothesis_results(hypothesis_results)

        report.add_images("Visualizations", image_paths)
        report.add_insights("Automated Insights", insights.get_insights())
        report.add_insights("Recommendations", insights.recommendations())

        outputs = {}
        outputs["markdown"] = report.save_markdown("eda_report.md")
        if self.args.pdf:
            outputs["pdf"] = report.save_pdf("eda_report.pdf")
        if self.args.excel:
            outputs["excel"] = report.save_excel("eda_report.xlsx")
        if self.args.csv:
            outputs["csv"] = report.save_csv_summary("eda_summary.csv")

        for fmt, path in outputs.items():
            logger.info(f"{fmt.upper()} report saved to {path}")
        self.report_outputs = outputs


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the EDA pipeline: cleaning, analysis, charts, and reports."
    )
    parser.add_argument("--dataset", type=str, default=config.DEFAULT_DATASET_PATH,
                         help="Path to the dataset (CSV/Excel/JSON). Defaults to the bundled sample dataset.")
    parser.add_argument("--report", action="store_true", help="Generate reports only.")
    parser.add_argument("--charts", action="store_true", help="Generate charts only.")
    parser.add_argument("--all", action="store_true", help="Run the full pipeline (default if no flags given).")
    parser.add_argument("--skip-clean", action="store_true", help="Skip the data-cleaning stage.")
    parser.add_argument("--no-pdf", dest="pdf", action="store_false", help="Skip PDF report generation.")
    parser.add_argument("--no-excel", dest="excel", action="store_false", help="Skip Excel report generation.")
    parser.add_argument("--no-csv", dest="csv", action="store_false", help="Skip CSV summary generation.")
    parser.set_defaults(pdf=True, excel=True, csv=True)

    args = parser.parse_args(argv)

    # If neither --report nor --charts was explicitly requested, run everything.
    if not args.report and not args.charts:
        args.report = True
        args.charts = True
    return args


def main():
    config.ensure_directories()
    args = parse_args()
    try:
        pipeline = EDAPipeline(args.dataset, config.CHARTS_DIR, config.REPORTS_DIR, args)
        pipeline.run()
        print("\n✅ EDA pipeline completed successfully.")
        if args.charts:
            print(f"🖼️  Charts: {config.CHARTS_DIR}/*.png")
        if args.report and hasattr(pipeline, "report_outputs"):
            for fmt, path in pipeline.report_outputs.items():
                print(f"📄 {fmt.upper()} report: {path}")
        print(f"📝 Logs: {os.path.join(config.LOGS_DIR, config.LOG_FILE_NAME)}")
    except Exception as e:
        logger.error(f"Fatal error in pipeline: {e}")
        logger.debug(traceback.format_exc())
        print(f"\n[FATAL ERROR] The pipeline failed: {e}")
        print(f"See {os.path.join(config.LOGS_DIR, config.LOG_FILE_NAME)} for full details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
