"""
dashboard.py
-------------
Interactive Streamlit dashboard for exploring the e-commerce sales dataset.

Run with:
    streamlit run dashboard.py
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.insert(0, os.path.dirname(__file__))

from src.data_loader import DataLoader, DataLoadError
from src.logger_config import get_logger

logger = get_logger("dashboard")

st.set_page_config(page_title="E-Commerce Sales Dashboard", layout="wide", page_icon="📊")

DATA_PATH = os.path.join("data", "sample_dataset.csv")


@st.cache_data(show_spinner="Loading dataset...")
def load_data():
    try:
        loader = DataLoader(DATA_PATH)
        return loader.load(clean=True)
    except DataLoadError as e:
        logger.error(f"Dashboard failed to load data: {e}")
        st.error(f"Could not load dataset: {e}")
        st.stop()


def main():
    st.title("📊 E-Commerce Sales — Interactive Dashboard")
    st.caption("Built with Streamlit + Plotly | Data Visualization Portfolio Project")

    df = load_data()

    # ---------------- Sidebar filters ----------------
    st.sidebar.header("Filters")
    regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()),
                                      default=sorted(df["region"].unique()))
    categories = st.sidebar.multiselect("Category", sorted(df["category"].unique()),
                                         default=sorted(df["category"].unique()))
    date_range = st.sidebar.date_input(
        "Order Date Range",
        value=(df["order_date"].min(), df["order_date"].max()),
    )

    filtered = df[
        (df["region"].isin(regions)) &
        (df["category"].isin(categories))
    ]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered = filtered[(filtered["order_date"] >= start) & (filtered["order_date"] <= end)]

    if filtered.empty:
        st.warning("No data matches the selected filters. Please broaden your selection.")
        st.stop()

    # ---------------- KPI row ----------------
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Revenue", f"${filtered['revenue'].sum():,.0f}")
    col2.metric("Total Orders", f"{len(filtered):,}")
    col3.metric("Avg Order Value", f"${filtered['revenue'].mean():,.2f}")
    col4.metric("Avg Rating", f"{filtered['customer_rating'].mean():.2f} / 5")

    st.divider()

    # ---------------- Row 1: Trend + Category ----------------
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Monthly Revenue Trend")
        trend = filtered.set_index("order_date").resample("ME")["revenue"].sum().reset_index()
        fig = px.line(trend, x="order_date", y="revenue", markers=True,
                      labels={"order_date": "Month", "revenue": "Revenue"})
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Revenue by Category")
        cat_rev = filtered.groupby("category")["revenue"].sum().sort_values(ascending=True).reset_index()
        fig = px.bar(cat_rev, x="revenue", y="category", orientation="h",
                     labels={"revenue": "Total Revenue", "category": "Category"},
                     color="revenue", color_continuous_scale="Blues")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- Row 2: Region + Payment ----------------
    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Orders by Region")
        region_counts = filtered["region"].value_counts().reset_index()
        region_counts.columns = ["region", "orders"]
        fig = px.pie(region_counts, names="region", values="orders", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        st.subheader("Payment Method Distribution")
        pay_counts = filtered["payment_method"].value_counts().reset_index()
        pay_counts.columns = ["payment_method", "orders"]
        fig = px.bar(pay_counts, x="payment_method", y="orders", color="payment_method")
        st.plotly_chart(fig, use_container_width=True)

    # ---------------- Row 3: Scatter + Table ----------------
    st.subheader("Unit Price vs Customer Rating")
    sample = filtered.sample(min(2000, len(filtered)), random_state=1)
    fig = px.scatter(sample, x="unit_price", y="customer_rating", color="category",
                      opacity=0.6, labels={"unit_price": "Unit Price", "customer_rating": "Rating"})
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Filtered Data Sample")
    st.dataframe(filtered.head(200), use_container_width=True)

    st.sidebar.divider()
    st.sidebar.caption("Data Visualization Portfolio Project — Streamlit Dashboard")


if __name__ == "__main__":
    main()
