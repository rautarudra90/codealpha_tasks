# src/data_explorer.py

**Purpose**

Answers the "what does the data look like?" questions that should always
precede deeper analysis: shape, dtypes, missing values, duplicates, summary
statistics, categorical breakdowns, correlations, and feature relationships.

## Class: `DataExplorer`

```python
DataExplorer(df: pd.DataFrame)
```

### `structural_overview() -> dict`
`{n_rows, n_columns, columns, dtypes, memory_usage_mb}`

### `missing_value_report() -> pd.DataFrame`
Count and percentage of missing values per column, for columns with at
least one missing value, sorted descending.

### `duplicate_report() -> dict`
`{duplicate_rows, duplicate_pct}`

### `numeric_summary() -> pd.DataFrame`
`df.describe().T` — count, mean, std, min, quartiles, max for every
numeric column.

### `categorical_summary() -> dict`
Top-10 value counts for every object/category column.

### `correlation_matrix() -> pd.DataFrame`
Pearson correlation matrix of numeric columns.

### `feature_relationships(category_col: str, numeric_cols=None) -> pd.DataFrame`
Mean of each numeric column, grouped by a categorical column — e.g. average
revenue and rating per region. Returns an empty DataFrame (does not raise)
if `category_col` isn't present, so it's safe to call speculatively.

### `distribution_skew_kurtosis() -> pd.DataFrame`
Skewness and kurtosis for every numeric column — useful for spotting
non-normal distributions before choosing a statistical test or model.

## Example

```python
from src.data_explorer import DataExplorer

explorer = DataExplorer(df)
overview = explorer.structural_overview()
relationships = explorer.feature_relationships("region", ["revenue", "customer_rating"])
```
