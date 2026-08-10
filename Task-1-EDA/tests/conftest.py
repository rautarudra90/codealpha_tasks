"""
conftest.py
------------
Shared pytest fixtures for the test suite. Uses a small synthetic
DataFrame instead of the full sample dataset so tests run fast and
their expected values are easy to reason about.
"""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """A small, deliberately imperfect DataFrame for testing the pipeline."""
    rng = np.random.default_rng(42)
    n = 60
    df = pd.DataFrame({
        "order_id": [f"ORD{i:04d}" for i in range(n)],
        "order_date": pd.date_range("2024-01-01", periods=n, freq="D"),
        "category": rng.choice(["Electronics", "Books", "Clothing"], size=n),
        "unit_price": rng.uniform(5, 500, size=n).round(2),
        "quantity": rng.integers(1, 5, size=n),
        "discount_pct": rng.choice([0, 5, 10, 20], size=n),
        "customer_age": rng.integers(18, 70, size=n),
        "customer_rating": rng.uniform(1, 5, size=n).round(1),
        "region": rng.choice(["North", "South", "East", "West"], size=n),
        "payment_method": rng.choice(["Credit Card", "PayPal", "Cash"], size=n),
    })
    df["revenue"] = (df["unit_price"] * df["quantity"] * (1 - df["discount_pct"] / 100)).round(2)

    # Inject realistic imperfections: duplicates, missing values, an outlier.
    df = pd.concat([df, df.iloc[[0]]], ignore_index=True)  # duplicate row
    df.loc[5, "customer_rating"] = np.nan
    df.loc[10, "region"] = np.nan
    df.loc[15, "revenue"] = 999999.0  # extreme outlier
    return df


@pytest.fixture
def messy_columns_df() -> pd.DataFrame:
    """A DataFrame with messy column names and string-encoded numbers."""
    return pd.DataFrame({
        " Order ID ": [1, 2, 3],
        "Unit-Price ($)": ["$10.50", "$20.00", "$5.25"],
        "Discount %": ["5%", "10%", "0%"],
    })
