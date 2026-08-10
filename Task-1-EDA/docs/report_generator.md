# src/report_generator.py

**Purpose**

Compiles all EDA findings into a professional report available in four
formats — Markdown, PDF, Excel, and CSV — from a single shared internal
list of structured sections, so every format stays in sync automatically:
add a section once, and it shows up everywhere.

## Class: `ReportGenerator`

```python
ReportGenerator(output_dir: str = "output")
```

### Content builders (format-agnostic)

| Method | Adds |
|---|---|
| `add_title(title)` | Report title + generation timestamp |
| `add_section(heading, content)` | Free-text section (Markdown-flavored) |
| `add_dataframe(heading, df)` | A table |
| `add_dict_as_table(heading, data, col_names=("Metric","Value"))` | A key/value table (ints are formatted with thousands separators so they don't get silently upcast to float) |
| `add_hypothesis_results(results)` | Formatted hypothesis-test results block |
| `add_insights(heading, insights)` | Bullet list of insight strings |
| `add_images(heading, image_paths)` | Chart images (Markdown: inline links; PDF: full pages) |

### Export methods

| Method | Output |
|---|---|
| `save_markdown(filename="eda_report.md")` | `.md` file, renders nicely on GitHub |
| `save_pdf(filename="eda_report.pdf")` | Polished PDF via ReportLab — tables auto-wrap and fit the page width, images get their own page |
| `save_excel(filename="eda_report.xlsx")` | `.xlsx` with a `Summary` sheet plus one sheet per table section |
| `save_csv_summary(filename="eda_summary.csv")` | Every table section combined into one long-format CSV with a `_section` column |
| `save_all(base_filename="eda_report")` | Generates all four at once, returns `{format: path}` |
| `save(filename="eda_report.md")` | Alias for `save_markdown` (backward-compatible entry point) |

## Example

```python
from src.report_generator import ReportGenerator

report = ReportGenerator(output_dir="output/reports")
report.add_title("EDA Report — sales.csv")
report.add_section("Executive Summary", "This dataset contains ...")
report.add_dataframe("Numeric Summary", numeric_summary_df)
report.add_insights("Automated Insights", insights_list)

outputs = report.save_all()
# {"markdown": "...", "pdf": "...", "excel": "...", "csv": "..."}
```

## Implementation notes

- PDF tables wrap cell text in `reportlab.platypus.Paragraph` and divide a
  fixed page width evenly across columns, so wide tables (e.g. a 7-column
  correlation matrix) never overflow the page.
- `NaN` values in tables are rendered as empty cells rather than the string
  `"nan"`.
- Excel sheet names are sanitized to Excel's 31-character limit and
  de-duplicated automatically.
