# src/data_loader.py

**Purpose**

Reads a dataset from disk and validates it before anything else touches it,
so a bad input fails immediately with a clear message instead of crashing
deep inside the analysis pipeline.

## Class: `DataLoader`

```python
DataLoader(filepath: str, date_columns: list[str] | None = None)
```

- `filepath` — path to a `.csv`, `.xlsx`, `.xls`, or `.json` file.
- `date_columns` — columns to parse as dates. Defaults to `["order_date"]`
  for backward compatibility with the sample dataset; pass `[]` to disable
  date parsing entirely, or a custom list for other datasets.

### `load() -> pd.DataFrame`

Auto-detects the file format from its extension and loads it. Raises
`DataLoadError` for any of the following, each with a specific message:

- File does not exist
- File exists but is 0 bytes
- File extension isn't one of `.csv/.xlsx/.xls/.json`
- File content is corrupted / unparseable
- Parsed result has 0 rows or 0 columns

Only date columns that actually exist in the file are parsed as dates —
passing a dataset without an `order_date` column will not raise an error.

## Exception: `DataLoadError`

Raised by `load()`. Always carries a human-readable message suitable for
displaying directly to an end user (this is what the CLI and the Streamlit
dashboard both show in their error paths).

## Example

```python
from src.data_loader import DataLoader, DataLoadError

try:
    df = DataLoader("data/raw/sample_dataset.csv").load()
except DataLoadError as e:
    print(f"Could not load dataset: {e}")
```
