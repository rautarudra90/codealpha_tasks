"""Tests for src/data_loader.py"""

import os
import pandas as pd
import pytest

from src.data_loader import DataLoader, DataLoadError


def test_load_valid_csv(tmp_path, sample_df):
    path = tmp_path / "data.csv"
    sample_df.to_csv(path, index=False)

    df = DataLoader(str(path)).load()

    assert not df.empty
    assert list(df.columns) == list(sample_df.columns)
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"])


def test_load_missing_file_raises(tmp_path):
    missing_path = tmp_path / "does_not_exist.csv"
    with pytest.raises(DataLoadError, match="not found"):
        DataLoader(str(missing_path)).load()


def test_load_empty_file_raises(tmp_path):
    empty_path = tmp_path / "empty.csv"
    empty_path.write_text("")
    with pytest.raises(DataLoadError):
        DataLoader(str(empty_path)).load()


def test_load_csv_with_only_header_raises(tmp_path):
    path = tmp_path / "header_only.csv"
    path.write_text("col_a,col_b\n")
    with pytest.raises(DataLoadError, match="empty"):
        DataLoader(str(path)).load()


def test_load_unsupported_format_raises(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("not a real dataset")
    with pytest.raises(DataLoadError, match="Unsupported file format"):
        DataLoader(str(path)).load()


def test_load_corrupted_file_raises(tmp_path):
    path = tmp_path / "corrupt.xlsx"
    path.write_bytes(b"this is not a valid xlsx file")
    with pytest.raises(DataLoadError):
        DataLoader(str(path)).load()


def test_load_excel(tmp_path, sample_df):
    path = tmp_path / "data.xlsx"
    sample_df.to_excel(path, index=False)

    df = DataLoader(str(path)).load()

    assert not df.empty
    assert df.shape[1] == sample_df.shape[1]


def test_load_json(tmp_path, sample_df):
    path = tmp_path / "data.json"
    sample_df.drop(columns=["order_date"]).to_json(path, orient="records")

    df = DataLoader(str(path), date_columns=[]).load()

    assert not df.empty
