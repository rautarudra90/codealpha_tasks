# src/insights_generator.py

**Purpose**

Turns numeric EDA output (correlations, group-bys, outlier counts) into
plain-English business insights and recommendations. This is what makes
the report readable by someone who doesn't want to interpret a correlation
matrix themselves.

Every insight is derived directly from the data passed in — nothing is
hardcoded to the sample e-commerce schema — and every builder method
degrades gracefully (skips silently) when its required columns aren't
present.

## Class: `InsightsGenerator`

```python
InsightsGenerator(df: pd.DataFrame)
```

All builder methods return `self`, so they can be chained.

### Builder methods

| Method | Produces |
|---|---|
| `category_performance(category_col, value_col)` | Best- and worst-performing category by summed value |
| `correlation_highlights(correlation, top_n=2)` | Strongest positive/negative correlations above \|r\| > 0.3 |
| `trend_analysis(date_col, value_col)` | First-half vs second-half percentage change over time |
| `outlier_summary(outlier_summary_df)` | Which column has the most outliers |
| `data_quality_summary(missing_report, duplicate_report)` | Worst missing-value column, duplicate row count |

### `recommendations() -> list[str]`
General, always-applicable recommendations (clean flagged issues, verify
correlations aren't confounded, review outliers individually).

### `get_insights() -> list[str]`
All collected insights so far, or a one-item fallback list if nothing was
found.

### `get_report_text() -> str`
The same insights rendered as a Markdown bullet list.

## Example

```python
from src.insights_generator import InsightsGenerator

insights = (
    InsightsGenerator(df)
    .category_performance("category", "revenue")
    .correlation_highlights(correlation_matrix)
    .data_quality_summary(missing_report, duplicate_report)
)
print(insights.get_report_text())
```
