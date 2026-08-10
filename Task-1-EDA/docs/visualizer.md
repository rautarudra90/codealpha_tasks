# src/visualizer.py

**Purpose**

Generates a professional suite of charts and saves them as PNG files. Every
chart method checks that its required columns exist before drawing
anything, so `generate_all()` degrades gracefully on datasets that don't
match the bundled sample schema instead of crashing.

## Class: `EDAVisualizer`

```python
EDAVisualizer(df: pd.DataFrame, output_dir: str = "output")
```

### Chart methods

| Method | Chart type |
|---|---|
| `plot_revenue_distribution(column="revenue")` | Histogram + KDE, 99th-percentile clipped |
| `plot_boxplot_by_category(category_col, value_col)` | Box plot |
| `plot_violin_by_category(category_col, value_col)` | Violin plot |
| `plot_correlation_heatmap()` | Heatmap of numeric correlations |
| `plot_scatter(x_col, y_col, hue_col)` | Scatter plot (sampled up to 1,000 points) |
| `plot_pairplot(columns=None, hue_col=None, sample_size=500)` | Seaborn pair plot (auto-caps to 5 numeric columns) |
| `plot_count(column="region")` | Count / bar plot |
| `plot_pie(column, top_n=6)` | Pie chart of top categories |
| `plot_bar_aggregate(category_col, value_col, agg="sum")` | Aggregated bar chart |
| `plot_time_trend(date_col, value_col, freq="ME")` | Line chart over time (requires a real datetime column) |

Every method returns the saved file path, or `None` if it was skipped
because a required column was missing.

### `generate_all() -> list[str]`

Runs the full standard chart suite with a `tqdm` progress bar, skipping any
chart that can't be built and logging why, and continuing with the rest
even if one chart raises an exception. Returns the list of paths that were
actually saved.

## Example

```python
from src.visualizer import EDAVisualizer

viz = EDAVisualizer(df, output_dir="output/charts")
paths = viz.generate_all()
```
