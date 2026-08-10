"""
dashboard.py
-------------
Streamlit dashboard for the EDA project. Provides an interactive UI on top
of the same src/ modules used by the CLI pipeline (main.py) - no analysis
logic is duplicated here, this file is purely presentation.

Run with:
    streamlit run dashboard.py
"""

import io
import os

import pandas as pd
import streamlit as st
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

import config
from src.data_loader import DataLoader, DataLoadError
from src.data_cleaner import DataCleaner
from src.data_explorer import DataExplorer
from src.anomaly_detector import AnomalyDetector
from src.hypothesis_tester import HypothesisTester
from src.insights_generator import InsightsGenerator
from src.report_generator import ReportGenerator

st.set_page_config(
    page_title="EDA Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Theme toggle (dark theme support)
# ---------------------------------------------------------------------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

DARK_CSS = """
<style>
.stApp { background-color: #0E1117; color: #FAFAFA; }
[data-testid="stMetric"] { background-color: #1B1F27; padding: 12px; border-radius: 10px; }
</style>
"""
LIGHT_CSS = """
<style>
[data-testid="stMetric"] { background-color: #F0F4F8; padding: 12px; border-radius: 10px; }
</style>
"""


def _load_dataframe(uploaded_file) -> pd.DataFrame:
    """Persist the uploaded file to disk and reuse the shared DataLoader."""
    suffix = os.path.splitext(uploaded_file.name)[1]
    temp_path = os.path.join(config.PROCESSED_DATA_DIR, f"_uploaded{suffix}")
    os.makedirs(config.PROCESSED_DATA_DIR, exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return DataLoader(temp_path).load()


def main():
    config.ensure_directories()
    st.markdown(DARK_CSS if st.session_state.dark_mode else LIGHT_CSS, unsafe_allow_html=True)

    st.sidebar.title("📊 EDA Analytics Suite")
    st.session_state.dark_mode = st.sidebar.toggle("Dark theme", value=st.session_state.dark_mode)

    st.sidebar.markdown("### 1. Dataset")
    uploaded_file = st.sidebar.file_uploader(
        "Upload a dataset", type=["csv", "xlsx", "xls", "json"]
    )
    use_sample = st.sidebar.checkbox("Use bundled sample dataset", value=uploaded_file is None)

    try:
        if uploaded_file is not None and not use_sample:
            df = _load_dataframe(uploaded_file)
            dataset_label = uploaded_file.name
        else:
            df = DataLoader(config.DEFAULT_DATASET_PATH).load()
            dataset_label = "sample_dataset.csv"
    except DataLoadError as e:
        st.error(f"Could not load dataset: {e}")
        st.stop()

    st.sidebar.markdown("### 2. Cleaning")
    apply_cleaning = st.sidebar.checkbox("Apply automatic cleaning", value=True)
    if apply_cleaning:
        cleaner = DataCleaner(df)
        cleaner.run_full_cleaning()
        df = cleaner.get_cleaned_data()
        cleaning_report = cleaner.get_report()
    else:
        cleaning_report = None

    st.sidebar.markdown("### 3. Filters")
    filtered_df = df.copy()
    categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
    if categorical_cols:
        filter_col = st.sidebar.selectbox("Filter by column", ["(none)"] + categorical_cols)
        if filter_col != "(none)":
            options = sorted(df[filter_col].dropna().unique().tolist())
            selected = st.sidebar.multiselect(f"Values in {filter_col}", options, default=options)
            filtered_df = filtered_df[filtered_df[filter_col].isin(selected)]

    numeric_cols = filtered_df.select_dtypes(include="number").columns.tolist()

    # ------------------------------------------------------------------
    # Header + summary cards
    # ------------------------------------------------------------------
    st.title("Exploratory Data Analysis Dashboard")
    st.caption(f"Dataset: **{dataset_label}**")

    explorer = DataExplorer(filtered_df)
    overview = explorer.structural_overview()
    missing_report = explorer.missing_value_report()
    duplicate_report = explorer.duplicate_report()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", f"{overview['n_rows']:,}")
    c2.metric("Columns", overview["n_columns"])
    c3.metric("Missing Values", f"{int(missing_report['missing_count'].sum()) if not missing_report.empty else 0}")
    c4.metric("Duplicate Rows", duplicate_report["duplicate_rows"])

    tabs = st.tabs([
        "Overview", "Charts", "Correlation", "Outliers",
        "Hypothesis Tests", "Insights", "Reports"
    ])

    # ------------------------------------------------------------------
    with tabs[0]:
        st.subheader("Data Preview")
        st.dataframe(filtered_df.head(50), use_container_width=True)

        st.subheader("Numeric Summary")
        st.dataframe(explorer.numeric_summary().round(2), use_container_width=True)

        if not missing_report.empty:
            st.subheader("Missing Values")
            st.dataframe(missing_report, use_container_width=True)

        if cleaning_report:
            st.subheader("Cleaning Summary")
            st.json({k: v for k, v in cleaning_report.items() if k != "missing_values_before"})

    # ------------------------------------------------------------------
    with tabs[1]:
        st.subheader("Distributions & Relationships")
        col_a, col_b = st.columns(2)

        with col_a:
            if numeric_cols:
                col = st.selectbox("Histogram column", numeric_cols, key="hist_col")
                fig, ax = plt.subplots()
                sns.histplot(filtered_df[col].dropna(), kde=True, ax=ax, color="#2E86AB")
                st.pyplot(fig)

        with col_b:
            if categorical_cols:
                col = st.selectbox("Count plot column", categorical_cols, key="count_col")
                fig, ax = plt.subplots()
                counts = filtered_df[col].value_counts().head(15)
                sns.barplot(x=counts.values, y=counts.index, ax=ax, hue=counts.index,
                            palette="mako", legend=False)
                st.pyplot(fig)

        if len(numeric_cols) >= 2 and categorical_cols:
            st.subheader("Box Plot by Category")
            num_col = st.selectbox("Numeric column", numeric_cols, key="box_num")
            cat_col = st.selectbox("Category column", categorical_cols, key="box_cat")
            fig, ax = plt.subplots(figsize=(9, 4))
            sns.boxplot(data=filtered_df, x=cat_col, y=num_col, ax=ax,
                        hue=cat_col, palette="viridis", legend=False, showfliers=False)
            ax.tick_params(axis="x", rotation=30)
            st.pyplot(fig)

    # ------------------------------------------------------------------
    with tabs[2]:
        st.subheader("Correlation Heatmap")
        if len(numeric_cols) >= 2:
            corr = filtered_df[numeric_cols].corr(numeric_only=True)
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
            st.pyplot(fig)
        else:
            st.info("Need at least two numeric columns to compute a correlation heatmap.")

    # ------------------------------------------------------------------
    with tabs[3]:
        st.subheader("Outlier Detection")
        detector = AnomalyDetector(filtered_df)
        selected_numeric = [c for c in config.DEFAULT_NUMERIC_COLUMNS if c in numeric_cols] or numeric_cols
        if selected_numeric:
            comparison = detector.compare_methods(selected_numeric)
            st.dataframe(comparison, use_container_width=True)
            st.caption(
                "IQR and Z-score are univariate (one column at a time). "
                "Isolation Forest looks at all selected columns together and can "
                "catch anomalies that look normal on any single column."
            )
        logical = detector.logical_anomalies()
        if logical:
            st.subheader("Domain-Rule Anomalies")
            for key, frame in logical.items():
                st.write(f"**{key}**: {len(frame)} rows flagged")

    # ------------------------------------------------------------------
    with tabs[4]:
        st.subheader("Hypothesis Tests")
        tester = HypothesisTester(filtered_df, alpha=config.HYPOTHESIS_ALPHA)
        results = tester.run_all()
        if results:
            for r in results:
                with st.expander(r["test_name"]):
                    st.write(f"Statistic: `{r['statistic']}`")
                    st.write(f"p-value: `{r['p_value']}`")
                    st.write(f"**{r['conclusion']}**")
        else:
            st.info("This dataset doesn't have the columns needed for the built-in hypothesis tests.")

    # ------------------------------------------------------------------
    with tabs[5]:
        st.subheader("Automated Insights")
        generator = InsightsGenerator(filtered_df)
        generator.data_quality_summary(missing_report, duplicate_report)
        if len(numeric_cols) >= 2:
            generator.correlation_highlights(filtered_df[numeric_cols].corr(numeric_only=True))
        if selected_numeric:
            generator.outlier_summary(detector.summary(selected_numeric))
        for cat_col in categorical_cols[:1]:
            for num_col in numeric_cols[:1]:
                generator.category_performance(cat_col, num_col)
        for insight in generator.get_insights():
            st.markdown(f"- {insight}")

    # ------------------------------------------------------------------
    with tabs[6]:
        st.subheader("Download Reports")
        st.write("Generate a report bundle from the current filtered data and download it below.")
        if st.button("Generate reports"):
            with st.spinner("Building reports..."):
                report = ReportGenerator(output_dir=config.REPORTS_DIR)
                report.add_title(f"{config.REPORT_TITLE} — {dataset_label}")
                report.add_dict_as_table("Dataset Information", {
                    "Rows": overview["n_rows"], "Columns": overview["n_columns"],
                    "Memory Usage (MB)": overview["memory_usage_mb"],
                })
                report.add_dataframe("Numeric Summary", explorer.numeric_summary().round(2))
                if len(numeric_cols) >= 2:
                    report.add_dataframe("Correlation Matrix",
                                          filtered_df[numeric_cols].corr(numeric_only=True).round(2))
                outputs = {
                    "Markdown": report.save_markdown("dashboard_report.md"),
                    "PDF": report.save_pdf("dashboard_report.pdf"),
                    "Excel": report.save_excel("dashboard_report.xlsx"),
                }
            st.success("Reports generated.")
            for fmt, path in outputs.items():
                with open(path, "rb") as f:
                    st.download_button(f"Download {fmt}", f.read(), file_name=os.path.basename(path))


if __name__ == "__main__":
    main()
