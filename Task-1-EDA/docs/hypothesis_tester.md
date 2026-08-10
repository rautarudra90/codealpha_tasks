# src/hypothesis_tester.py

**Purpose**

Runs formal statistical hypothesis tests to validate assumptions about the
dataset, and explains each result in plain terms (statistic, p-value,
reject/fail-to-reject H0).

## Class: `HypothesisTester`

```python
HypothesisTester(df: pd.DataFrame, alpha: float = 0.05)
```

### Individual tests

| Method | Test | Requires columns |
|---|---|---|
| `test_anova_region_revenue()` | One-way ANOVA — does mean revenue differ across regions? | `region`, `revenue` |
| `test_correlation_price_rating()` | Pearson correlation — is there a linear relationship between price and rating? | `unit_price`, `customer_rating` |
| `test_ttest_discounted_vs_full_price_revenue()` | Welch's t-test — does revenue differ between discounted and full-price orders? | `discount_pct`, `revenue` |
| `test_chi_square_category_payment()` | Chi-square test of independence — are category and payment method associated? | `category`, `payment_method` |

Each returns a dict:
`{test_name, statistic, p_value, alpha, significant, conclusion}`.

### `run_all() -> list[dict]`

Runs every test above, but **skips** (does not crash on) any test whose
required columns aren't present in the dataset — this is what makes the
tester usable on datasets other than the bundled sample. If a test raises
an unexpected error it's also skipped and logged, rather than taking down
the whole pipeline.

## Example

```python
from src.hypothesis_tester import HypothesisTester

tester = HypothesisTester(df, alpha=0.05)
results = tester.run_all()
for r in results:
    print(r["test_name"], "->", r["conclusion"])
```
