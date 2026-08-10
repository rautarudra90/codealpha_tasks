"""Tests for src/data_cleaner.py"""

import pandas as pd
from src.data_cleaner import DataCleaner


def test_remove_duplicates(sample_df):
    n_dupes_before = sample_df.duplicated().sum()
    assert n_dupes_before > 0  # fixture is designed to include one

    cleaner = DataCleaner(sample_df).remove_duplicates()

    assert cleaner.get_cleaned_data().duplicated().sum() == 0
    assert cleaner.report["duplicates_removed"] == n_dupes_before


def test_standardize_column_names(messy_columns_df):
    cleaner = DataCleaner(messy_columns_df).standardize_column_names()
    cleaned = cleaner.get_cleaned_data()

    assert "order_id" in cleaned.columns
    assert "unit_price" in cleaned.columns
    assert "discount" in cleaned.columns
    assert all(" " not in col for col in cleaned.columns)


def test_detect_and_fix_dtypes(messy_columns_df):
    cleaner = (
        DataCleaner(messy_columns_df)
        .standardize_column_names()
        .detect_and_fix_dtypes()
    )
    cleaned = cleaner.get_cleaned_data()

    assert pd.api.types.is_numeric_dtype(cleaned["unit_price"])
    assert cleaned["unit_price"].iloc[0] == 10.50


def test_handle_missing_values_numeric_median(sample_df):
    cleaner = DataCleaner(sample_df)
    cleaner.handle_missing_values(numeric_strategy="median")
    cleaned = cleaner.get_cleaned_data()

    assert cleaned["customer_rating"].isnull().sum() == 0


def test_handle_missing_values_categorical(sample_df):
    cleaner = DataCleaner(sample_df)
    cleaner.handle_missing_values(categorical_strategy="unknown")
    cleaned = cleaner.get_cleaned_data()

    assert cleaned["region"].isnull().sum() == 0
    assert "Unknown" in cleaned["region"].values


def test_handle_outliers_cap_preserves_row_count(sample_df):
    original_len = len(sample_df)
    cleaner = DataCleaner(sample_df).handle_outliers(columns=["revenue"], method="cap")
    cleaned = cleaner.get_cleaned_data()

    assert len(cleaned) == original_len
    assert cleaned["revenue"].max() < 999999.0


def test_handle_outliers_remove_drops_rows(sample_df):
    cleaner = DataCleaner(sample_df).handle_outliers(columns=["revenue"], method="remove")
    cleaned = cleaner.get_cleaned_data()

    assert 999999.0 not in cleaned["revenue"].values
    assert len(cleaned) < len(sample_df)


def test_run_full_cleaning_end_to_end(sample_df):
    cleaner = DataCleaner(sample_df).run_full_cleaning()
    cleaned = cleaner.get_cleaned_data()
    report = cleaner.get_report()

    assert cleaned.duplicated().sum() == 0
    assert cleaned.isnull().sum().sum() == 0
    assert report["final_shape"] == cleaned.shape
    assert report["original_shape"] == sample_df.shape


def test_optimize_memory_reduces_or_maintains_usage(sample_df):
    cleaner = DataCleaner(sample_df).run_full_cleaning()
    report = cleaner.get_report()

    assert "memory_optimization_mb" in report
    assert report["memory_optimization_mb"]["after"] <= report["memory_optimization_mb"]["before"]
