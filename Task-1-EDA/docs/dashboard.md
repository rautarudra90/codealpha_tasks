# dashboard.py — Streamlit Dashboard

**Purpose**

Interactive UI on top of the same `src/` modules used by the CLI — no
analysis logic is duplicated; `dashboard.py` is purely presentation.

## Run it

```bash
streamlit run dashboard.py
```

Opens at `http://localhost:8501` by default.

## Features

- **Upload dataset** — CSV/Excel/JSON, or use the bundled sample dataset.
- **Automatic cleaning toggle** — runs the same `DataCleaner` pipeline as
  the CLI, on or off.
- **Interactive filters** — filter rows by any categorical column's values.
- **Summary cards** — row count, column count, missing values, duplicate
  rows, updated live as filters change.
- **Tabs**:
  - *Overview* — data preview, numeric summary, missing values, cleaning report.
  - *Charts* — interactive histogram, count plot, and box plot with
    column pickers.
  - *Correlation* — correlation heatmap.
  - *Outliers* — IQR / Z-score / Isolation Forest comparison table, plus
    domain-rule anomalies.
  - *Hypothesis Tests* — expandable cards with statistic, p-value, and
    conclusion for each applicable test.
  - *Insights* — the same plain-English insights the CLI puts in reports.
  - *Reports* — generate and download Markdown/PDF/Excel reports for the
    currently filtered view.
- **Dark theme** — toggle in the sidebar.

## Notes

- Uploaded files are written to `data/processed/_uploaded.<ext>` before
  being read through the shared `DataLoader`, so the same validation and
  error handling used by the CLI applies here too.
- Hypothesis tests and some insight builders only run when the filtered
  dataset actually has the columns they need — the tabs display an
  informational message instead of an error when that's not the case.
