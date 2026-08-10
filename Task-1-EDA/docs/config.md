# config.py

**Purpose**

Single source of truth for every path and setting used across the project.
No other module hardcodes a folder name or a magic threshold — they all
import from here. This means renaming an output folder, changing the
significance level for hypothesis tests, or pointing at a new default
dataset is a one-line change instead of a project-wide search-and-replace.

## Key values

| Name | Meaning | Default |
|---|---|---|
| `RAW_DATA_DIR` | Where input datasets live | `data/raw` |
| `PROCESSED_DATA_DIR` | Where cleaned datasets are written | `data/processed` |
| `CHARTS_DIR` | Where generated chart PNGs are saved | `output/charts` |
| `REPORTS_DIR` | Where generated reports are saved | `output/reports` |
| `LOGS_DIR` | Where the rotating log file lives | `output/logs` |
| `DEFAULT_DATASET_PATH` | Dataset used when `--dataset` isn't passed | `data/raw/sample_dataset.csv` |
| `RANDOM_STATE` | Seed used everywhere randomness matters (Isolation Forest, sampling) | `42` |
| `HYPOTHESIS_ALPHA` | Significance level for all hypothesis tests | `0.05` |
| `IQR_MULTIPLIER` | Tukey fence multiplier for IQR outlier detection | `1.5` |
| `ZSCORE_THRESHOLD` | \|z\| above this is flagged as an outlier | `3.0` |
| `ISOLATION_FOREST_CONTAMINATION` | Expected proportion of multivariate anomalies | `0.02` |

## Functions

### `ensure_directories() -> None`
Creates every directory the project writes to (`data/raw`, `data/processed`,
`output/charts`, `output/reports`, `output/logs`) if they don't already
exist. Called once at the start of `main.py` and `dashboard.py`.

## Example

```python
import config

print(config.DEFAULT_DATASET_PATH)
config.ensure_directories()
```
