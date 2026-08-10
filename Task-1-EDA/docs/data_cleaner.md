# src/data_cleaner.py

**Purpose**

Dedicated cleaning pipeline that runs after `DataLoader` and before any
analysis module. Every step is independent, chainable, and records what it
did into a structured report, so the whole pipeline stays inspectable and
individually testable.

## Class: `DataCleaner`

```python
DataCleaner(df: pd.DataFrame)
```

Works on an internal copy of `df` — the original DataFrame passed in is
never mutated.

### Chainable cleaning steps

Each method returns `self`, so steps can be chained fluently:

| Method | What it does |
|---|---|
| `standardize_column_names()` | Converts column names to `snake_case`; any run of non-alphanumeric characters (spaces, hyphens, `$`, `%`, parentheses...) becomes a single underscore. |
| `remove_duplicates()` | Drops fully duplicated rows. |
| `detect_and_fix_dtypes()` | Finds object columns that are actually numeric text (e.g. `"$1,200"`, `"45%"`) and converts them, only when >95% of values parse cleanly. |
| `convert_dates(date_columns=None)` | Converts likely date columns (name contains "date"/"time", or an explicit list) to real `datetime64` dtype. Only commits the conversion if >80% of values parse. |
| `handle_missing_values(numeric_strategy="median", categorical_strategy="mode")` | Fills numeric gaps with median/mean/zero, categorical gaps with mode/"Unknown", datetime gaps via forward/backward fill. |
| `handle_outliers(columns=None, method="cap", k=1.5)` | IQR-based outlier handling. `method="cap"` winsorizes (preserves row count); `method="remove"` drops offending rows. |
| `optimize_memory()` | Downcasts numeric dtypes (`int64→int32`, `float64→float32`) and converts low-cardinality object columns to `category`, vectorized, in one pass. |

### `run_full_cleaning(numeric_strategy="median", categorical_strategy="mode", outlier_method="cap") -> DataCleaner`

Runs the standard sequence: standardize names → remove duplicates → fix
dtypes → convert dates → handle missing values → handle outliers →
optimize memory.

### `get_cleaned_data() -> pd.DataFrame`
Returns the cleaned DataFrame.

### `get_report() -> dict`
Returns a dict describing every change made: `duplicates_removed`,
`missing_values_before`/`missing_values_handled`, `dtype_fixes`,
`columns_renamed`, `dates_converted`, `outliers_capped`,
`memory_optimization_mb`, `original_shape`, `final_shape`.

## Example

```python
from src.data_cleaner import DataCleaner

cleaner = DataCleaner(df).run_full_cleaning(outlier_method="cap")
clean_df = cleaner.get_cleaned_data()
report = cleaner.get_report()
print(report["duplicates_removed"], report["final_shape"])
```

Or step by step, for more control:

```python
cleaner = (
    DataCleaner(df)
    .standardize_column_names()
    .remove_duplicates()
    .handle_missing_values(numeric_strategy="mean")
)
```
