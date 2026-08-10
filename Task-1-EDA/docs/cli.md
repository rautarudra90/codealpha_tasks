# main.py — Command Line Interface

**Purpose**

Orchestrates the full pipeline: load → clean → explore → detect anomalies
→ test hypotheses → visualize → generate insights → report. Each stage is
independently timed and logged via `log_execution_time`.

## Usage

```bash
python main.py                          # run everything with defaults
python main.py --dataset file.csv       # use a specific dataset
python main.py --charts                 # charts only (no reports)
python main.py --report                 # reports only (no charts)
python main.py --all                    # explicit: run everything
python main.py --skip-clean             # analyze raw data, skip cleaning
python main.py --no-pdf --no-excel      # limit which report formats are generated
```

## Flags

| Flag | Effect |
|---|---|
| `--dataset PATH` | Dataset to analyze (CSV/Excel/JSON). Defaults to `data/raw/sample_dataset.csv`. |
| `--report` | Generate reports. If neither `--report` nor `--charts` is given, both run by default. |
| `--charts` | Generate charts. Same default behavior as above. |
| `--all` | Explicitly run the full pipeline (equivalent to the no-flags default). |
| `--skip-clean` | Skip the `DataCleaner` stage and analyze the raw data as loaded. |
| `--no-pdf` | Skip PDF report generation. |
| `--no-excel` | Skip Excel report generation. |
| `--no-csv` | Skip CSV summary generation. |

Markdown report generation always runs when `--report` is active — it's the
lightweight default output.

## Error handling

If the dataset can't be loaded (missing, empty, corrupted, or unsupported
format), the CLI prints a clear `[ERROR]` message and, if using the default
sample dataset path specifically, attempts to auto-regenerate it via
`data/generate_dataset.py` before giving up. Any other fatal error is
logged with a full traceback to the log file, and a `[FATAL ERROR]` summary
is printed to the console with a pointer to the log file. The process exits
with status code 1 on failure.

## Output

On success, prints the paths to every chart/report generated and the log
file location:

```
✅ EDA pipeline completed successfully.
🖼️  Charts: output/charts/*.png
📄 MARKDOWN report: output/reports/eda_report.md
📄 PDF report: output/reports/eda_report.pdf
📄 EXCEL report: output/reports/eda_report.xlsx
📄 CSV report: output/reports/eda_summary.csv
📝 Logs: output/logs/eda_project.log
```
