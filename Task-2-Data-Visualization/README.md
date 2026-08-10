# Data Visualization Project

A complete, professional data-visualization portfolio project featuring both
**static, publication-quality charts** (Matplotlib/Seaborn) and a **fully
interactive Streamlit + Plotly dashboard**, built on top of a realistic
e-commerce sales dataset.

---

## 📁 Project Structure

```
data_visualization_project/
├── data/
│   ├── generate_dataset.py     # Synthetic dataset generator (reproducible)
│   └── sample_dataset.csv      # Pre-generated 5,000+ row dataset
├── src/
│   ├── __init__.py
│   ├── logger_config.py        # Centralized rotating-file + console logging
│   ├── data_loader.py          # Loading + light cleaning of the dataset
│   ├── static_visualizer.py    # 7 static Matplotlib/Seaborn charts
│   └── story_builder.py        # Turns charts into a written data story
├── logs/                        # Rotating log files (auto-created)
├── output/                      # Generated charts + data story (auto-created)
├── screenshots/                 # Sample pre-generated chart images
├── main.py                      # Generates static charts + story report
├── dashboard.py                 # Interactive Streamlit + Plotly dashboard
├── requirements.txt
├── run.bat                      # One-click Windows setup + run
├── .gitignore
├── LICENSE
└── README.md
```

## 🎯 What This Project Delivers

### 1. Static Chart Suite (`python main.py`)
Seven portfolio-quality charts, each designed with a clear narrative purpose:

| # | Chart | Insight |
|---|---|---|
| 1 | Monthly Revenue Trend + Rolling Average | Growth trajectory over time |
| 2 | Revenue by Category (ranked bar) | Which categories drive the business |
| 3 | Region × Payment Method Heatmap | Regional payment behavior |
| 4 | Discount Impact (violin plot) | How discounting affects order value |
| 5 | Age Group Spending | Which age brackets spend the most |
| 6 | Rating Distribution | Overall customer satisfaction |
| 7 | Regional Order Share (donut) | Where order volume concentrates |

All charts are saved as high-resolution PNGs in `output/`, and a Markdown
**data story** (`output/data_story.md`) ties every chart to a business
insight and a recommended action — the kind of deliverable that supports
real decision-making, not just pretty pictures.

### 2. Interactive Dashboard (`streamlit run dashboard.py`)
A live, filterable Plotly-powered dashboard with:
- Sidebar filters for region, category, and date range
- KPI cards (total revenue, orders, average order value, average rating)
- Six interactive charts (trend, category bar, region pie, payment bar,
  price-vs-rating scatter) that respond instantly to filter changes
- A live, scrollable data table of the filtered results

## 🏗️ Architecture

Built with clean **object-oriented design**:

| Class | Responsibility |
|---|---|
| `DataLoader` | Loads and lightly cleans the dataset (drops duplicates/invalid rows) |
| `StaticVisualizer` | Generates each of the 7 static charts as a dedicated method |
| `StoryBuilder` | Computes key insights and writes the narrative Markdown report |
| `VisualizationPipeline` (in `main.py`) | Orchestrates the static-chart workflow end-to-end |

The Streamlit dashboard (`dashboard.py`) reuses the same `DataLoader` class,
so both the static and interactive experiences stay consistent with a single
source of truth for data loading and cleaning logic.

## ⚙️ Installation & Setup

### Requirements
- Python 3.9+

### Steps

```bash
# 1. Extract the ZIP file
cd data_visualization_project

# 2. Install dependencies
pip install -r requirements.txt

# 3a. Generate static charts + data story
python main.py

# 3b. OR launch the interactive dashboard
streamlit run dashboard.py
```

### Windows Quick Start
Double-click **`run.bat`** — it installs dependencies, then lets you choose
between the static pipeline and the interactive dashboard.

## ▶️ Expected Output

Running `python main.py`:
```
✅ Visualization pipeline completed successfully.
🖼️  Charts (7): output/*.png
📄 Data story: output/data_story.md
📝 Logs: logs/visualization_project.log

💡 Tip: run 'streamlit run dashboard.py' for the interactive dashboard.
```

Running `streamlit run dashboard.py` opens a browser tab at
`http://localhost:8501` with the live dashboard.

## 📊 Sample Outputs

Pre-generated sample charts are included in `screenshots/`:
- `01_revenue_trend.png`
- `02_category_revenue_ranked.png`
- `03_region_payment_heatmap.png`
- `04_discount_impact.png`
- `05_age_group_spending.png`
- `06_rating_distribution.png`
- `07_regional_share_donut.png`

The full data story narrative is generated at `output/data_story.md`.

## 📦 Dataset

The dataset (`data/sample_dataset.csv`) is synthetically generated to mirror
a realistic e-commerce sales log: 5,000+ orders, 8 categories, 5 regions, 5
payment methods, with genuine seasonal and category-driven correlations.
No internet connection or manual download is required. Regenerate a fresh
copy anytime with:

```bash
python data/generate_dataset.py
```

## 🛡️ Error Handling & Logging

- `DataLoader` raises a clear `DataLoadError` if the file is missing, empty,
  or unreadable — `main.py` catches this and auto-regenerates the dataset.
- All chart-generation steps are logged to `logs/visualization_project.log`
  (rotating, max 2 MB, 5 backups) as well as the console.
- The Streamlit dashboard uses `st.error()` and `st.stop()` to fail
  gracefully and informatively if data loading fails.

## 🧩 Extending This Project

- Add a new static chart by adding a method to `StaticVisualizer` and
  including it in `generate_all()`.
- Add a new dashboard panel by adding a new Plotly figure block to
  `dashboard.py`.
- Point `DATA_PATH` at your own CSV (matching the existing schema) to
  visualize real data instead of the synthetic sample.

## 📄 License

Released under the MIT License — see `LICENSE` for details.
