# src/anomaly_detector.py

**Purpose**

Detects statistical anomalies using three complementary methods, plus a
separate layer of business-rule sanity checks that no statistical method
can infer on its own.

## Class: `AnomalyDetector`

```python
AnomalyDetector(df: pd.DataFrame)
```

### Statistical methods

| Method | Type | Notes |
|---|---|---|
| `iqr_outliers(column, k=1.5)` | Univariate | Robust to non-normal distributions. Standard Tukey fence. |
| `zscore_outliers(column, threshold=3.0)` | Univariate | Assumes roughly normal data; returns empty if the column has zero variance. |
| `isolation_forest_outliers(columns=None, contamination=0.02)` | Multivariate | Considers combinations of columns at once — can catch a row that looks normal on every single feature but unusual as a whole. |

Each returns a `pd.DataFrame` of the flagged rows.

### `logical_anomalies() -> dict`
Domain-rule checks that only apply to the bundled e-commerce sample schema
(non-positive `delivery_days`, `customer_rating` outside 1–5, non-positive
`unit_price`). Returns `{check_name: DataFrame}` for every rule that found
at least one violation; only runs checks whose columns exist.

### `summary(numeric_columns=None) -> pd.DataFrame`
One row per column with IQR-based outlier count and percentage.

### `compare_methods(numeric_columns=None) -> pd.DataFrame`
Runs IQR, Z-score (per column) and Isolation Forest (across all given
columns together) side by side, so the differences between methods are
visible instead of hidden behind a single outlier count.

## Example

```python
from src.anomaly_detector import AnomalyDetector

detector = AnomalyDetector(df)
comparison = detector.compare_methods(["revenue", "unit_price", "customer_age"])
logical = detector.logical_anomalies()
```
