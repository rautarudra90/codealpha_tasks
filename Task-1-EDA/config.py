"""
config.py
----------
Single source of truth for paths, thresholds, and settings used across the
EDA project. Centralizing configuration here means every module (loader,
cleaner, visualizer, report generator, dashboard, CLI) references the same
values instead of hardcoding strings, which is what breaks projects when a
folder gets renamed or the dataset moves.
"""

import os

# ---------------------------------------------------------------------------
# Base paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")

OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CHARTS_DIR = os.path.join(OUTPUT_DIR, "charts")
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
LOGS_DIR = os.path.join(OUTPUT_DIR, "logs")

DEFAULT_DATASET_NAME = "sample_dataset.csv"
DEFAULT_DATASET_PATH = os.path.join(RAW_DATA_DIR, DEFAULT_DATASET_NAME)
CLEANED_DATASET_PATH = os.path.join(PROCESSED_DATA_DIR, "cleaned_dataset.csv")

LOG_FILE_NAME = "eda_project.log"

# ---------------------------------------------------------------------------
# Analysis settings
# ---------------------------------------------------------------------------
RANDOM_STATE = 42
HYPOTHESIS_ALPHA = 0.05          # significance level for hypothesis tests
IQR_MULTIPLIER = 1.5             # standard Tukey fence multiplier
ZSCORE_THRESHOLD = 3.0           # |z| above this is flagged as an outlier
ISOLATION_FOREST_CONTAMINATION = 0.02  # expected proportion of anomalies

# Columns checked for numeric outliers/anomaly detection by default.
# Overridable per-dataset from the CLI or dashboard.
DEFAULT_NUMERIC_COLUMNS = [
    "revenue", "unit_price", "delivery_days", "customer_age", "customer_rating"
]

# ---------------------------------------------------------------------------
# Visualization settings
# ---------------------------------------------------------------------------
CHART_DPI = 150
CHART_STYLE = "whitegrid"
CHART_PALETTE = "viridis"

# ---------------------------------------------------------------------------
# Report settings
# ---------------------------------------------------------------------------
REPORT_TITLE = "Exploratory Data Analysis Report"
COMPANY_NAME = "EDA Analytics Suite"


def ensure_directories() -> None:
    """Create every directory this project writes to, if not already present."""
    for directory in (
        RAW_DATA_DIR, PROCESSED_DATA_DIR, CHARTS_DIR, REPORTS_DIR, LOGS_DIR
    ):
        os.makedirs(directory, exist_ok=True)
