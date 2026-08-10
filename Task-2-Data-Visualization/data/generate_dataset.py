"""
generate_dataset.py
--------------------
Generates a realistic, synthetic e-commerce sales dataset for exploratory
data analysis. The dataset intentionally includes some missing values,
duplicate rows, outliers, and mild correlations so that the EDA pipeline
has genuine patterns and issues to discover.

Run directly to regenerate data/sample_dataset.csv:
    python data/generate_dataset.py
"""

import os
import numpy as np
import pandas as pd


def generate_dataset(n_rows: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Generate a synthetic e-commerce sales dataset.

    Args:
        n_rows (int): Number of records to generate.
        seed (int): Random seed for reproducibility.

    Returns:
        pd.DataFrame: The generated dataset.
    """
    rng = np.random.default_rng(seed)

    categories = ["Electronics", "Clothing", "Home & Kitchen", "Books",
                  "Sports", "Beauty", "Toys", "Groceries"]
    regions = ["North", "South", "East", "West", "Central"]
    payment_methods = ["Credit Card", "Debit Card", "PayPal", "Cash on Delivery", "UPI"]

    order_dates = pd.date_range("2023-01-01", "2024-12-31", freq="D")
    dates = rng.choice(order_dates, size=n_rows)

    category = rng.choice(categories, size=n_rows, p=[0.22, 0.18, 0.13, 0.09, 0.12, 0.10, 0.08, 0.08])

    # Base price depends on category to create realistic correlations.
    base_price_map = {
        "Electronics": 250, "Clothing": 45, "Home & Kitchen": 80, "Books": 18,
        "Sports": 60, "Beauty": 35, "Toys": 28, "Groceries": 15,
    }
    base_prices = np.array([base_price_map[c] for c in category])
    price = np.abs(rng.normal(loc=base_prices, scale=base_prices * 0.35))

    quantity = rng.integers(1, 6, size=n_rows)
    discount_pct = rng.choice([0, 5, 10, 15, 20, 25, 30], size=n_rows,
                               p=[0.35, 0.15, 0.15, 0.15, 0.1, 0.05, 0.05])
    discount = price * (discount_pct / 100)
    revenue = np.round((price - discount) * quantity, 2)

    customer_age = rng.integers(18, 70, size=n_rows)
    customer_rating = np.clip(rng.normal(loc=4.0, scale=0.9, size=n_rows), 1, 5).round(1)

    region = rng.choice(regions, size=n_rows)
    payment_method = rng.choice(payment_methods, size=n_rows,
                                 p=[0.35, 0.2, 0.2, 0.1, 0.15])

    delivery_days = np.abs(rng.normal(loc=4, scale=2, size=n_rows)).round().astype(int) + 1

    df = pd.DataFrame({
        "order_id": [f"ORD{100000 + i}" for i in range(n_rows)],
        "order_date": dates,
        "category": category,
        "unit_price": price.round(2),
        "quantity": quantity,
        "discount_pct": discount_pct,
        "revenue": revenue,
        "customer_age": customer_age,
        "customer_rating": customer_rating,
        "region": region,
        "payment_method": payment_method,
        "delivery_days": delivery_days,
    })

    # ---- Inject realistic data-quality issues on purpose ----

    # 1. Missing values in a few columns.
    for col, frac in [("customer_rating", 0.04), ("delivery_days", 0.02), ("unit_price", 0.01)]:
        idx = rng.choice(df.index, size=int(len(df) * frac), replace=False)
        df.loc[idx, col] = np.nan

    # 2. Duplicate rows (simulating logging errors).
    dup_rows = df.sample(n=int(n_rows * 0.01), random_state=seed)
    df = pd.concat([df, dup_rows], ignore_index=True)

    # 3. Outliers in revenue (data entry errors / bulk orders).
    outlier_idx = rng.choice(df.index, size=15, replace=False)
    df.loc[outlier_idx, "revenue"] = df.loc[outlier_idx, "revenue"] * rng.uniform(8, 15)

    # 4. A few negative delivery_days (impossible values -> anomalies to catch).
    bad_idx = rng.choice(df.index, size=5, replace=False)
    df.loc[bad_idx, "delivery_days"] = -1

    # Shuffle rows.
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    return df


def main():
    df = generate_dataset()
    out_path = os.path.join(os.path.dirname(__file__), "sample_dataset.csv")
    df.to_csv(out_path, index=False)
    print(f"Dataset generated: {out_path} ({len(df)} rows)")


if __name__ == "__main__":
    main()
