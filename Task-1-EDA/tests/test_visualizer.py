"""Tests for src/visualizer.py"""

import os
from src.visualizer import EDAVisualizer


def test_plot_revenue_distribution_saves_file(tmp_path, sample_df):
    viz = EDAVisualizer(sample_df, output_dir=str(tmp_path))
    path = viz.plot_revenue_distribution("revenue")

    assert path is not None
    assert os.path.exists(path)


def test_plot_skips_gracefully_when_column_missing(tmp_path, sample_df):
    viz = EDAVisualizer(sample_df, output_dir=str(tmp_path))
    path = viz.plot_boxplot_by_category("not_a_column", "revenue")

    assert path is None


def test_plot_correlation_heatmap_saves_file(tmp_path, sample_df):
    viz = EDAVisualizer(sample_df, output_dir=str(tmp_path))
    path = viz.plot_correlation_heatmap()

    assert path is not None
    assert os.path.exists(path)


def test_generate_all_produces_multiple_charts(tmp_path, sample_df):
    viz = EDAVisualizer(sample_df, output_dir=str(tmp_path))
    paths = viz.generate_all()

    assert len(paths) >= 5
    assert all(os.path.exists(p) for p in paths)


def test_generate_all_does_not_crash_on_minimal_dataset(tmp_path, sample_df):
    # Only one numeric column and no date/category columns at all.
    minimal_df = sample_df[["customer_age"]].copy()
    viz = EDAVisualizer(minimal_df, output_dir=str(tmp_path))

    paths = viz.generate_all()  # should not raise, just produce fewer charts
    assert isinstance(paths, list)
