import sys
import os

# Automatically find project root (no hardcoded path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from utils.db import get_connection

st.set_page_config(layout="wide")

st.title("💰 Profit & Loss Dashboard")
st.info(
    "Actual business profit calculated using buying price, selling price, "
    "quantity sold, and operational expenses."
)

# --------------------------------------------------
# LOAD DATA (ALWAYS FRESH)
# --------------------------------------------------
engine = get_connection()

profit_df = pd.read_sql(
    "SELECT * FROM vw_profit_analysis ORDER BY date",
    engine
)

profit_df["date"] = pd.to_datetime(profit_df["date"])

# --------------------------------------------------
# DATE HELPERS
# --------------------------------------------------
profit_df["year"] = profit_df["date"].dt.year
profit_df["month_name"] = profit_df["date"].dt.month_name()
profit_df["month_num"] = profit_df["date"].dt.month

# --------------------------------------------------
# FILTER SIDEBAR
# --------------------------------------------------
st.sidebar.header("🔍 Filters")

years = sorted(profit_df["year"].unique())

year = st.sidebar.selectbox(
    "Select Year",
    years,
    index=len(years)-1  # auto-select latest year
)

year_df = profit_df[profit_df["year"] == year]

available_months = (
    year_df
    .sort_values("month_num")["month_name"]
    .unique()
)

selected_months = st.sidebar.multiselect(
    "Select Month",
    available_months,
    default=available_months
)

if not selected_months:
    selected_months = available_months

fuel_types = profit_df["fuel_type"].unique()

fuel = st.sidebar.multiselect(
    "Fuel Type",
    fuel_types,
    default=fuel_types
)

# --------------------------------------------------
# FILTER CORE DATA
# --------------------------------------------------
filtered_df = profit_df[
    (profit_df["year"] == year) &
    (profit_df["month_name"].isin(selected_months)) &
    (profit_df["fuel_type"].isin(fuel))
]

# --------------------------------------------------
# HANDLE EMPTY SCENARIOS
# --------------------------------------------------
if filtered_df.empty:
    st.warning("⚠️ No financial data available for the selected period.")
    st.stop()


# --------------------------------------------------
# KPI CALCULATION (PRODUCTION GRADE)
# --------------------------------------------------
total_margin = filtered_df["fuel_margin"].sum()
total_expense = filtered_df["total_expenses"].sum()
total_profit = filtered_df["profit"].sum()

profit_margin_pct = (
    (total_profit / total_margin) * 100
    if total_margin != 0 else 0
)

# --------------------------------------------------
# KPI DISPLAY
# --------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Fuel Margin (₹)", f"{int(total_margin):,}")

with col2:
    st.metric("Total Expenses (₹)", f"{int(total_expense):,}")

with col3:
    st.metric("Actual Profit (₹)", f"{int(total_profit):,}")

with col4:
    st.metric("Profit Margin (%)", f"{profit_margin_pct:.2f}%")

# --------------------------------------------------
# PROFIT TREND
# --------------------------------------------------
st.subheader("📈 Profit Trend Over Time")

profit_trend = (
    filtered_df
    .groupby("date")["profit"]
    .sum()
)

st.line_chart(profit_trend, use_container_width=True)

# --------------------------------------------------
# FUEL-WISE PROFIT
# --------------------------------------------------
st.subheader("⛽ Fuel-wise Profit Distribution")

fuel_profit = filtered_df.groupby("fuel_type")["profit"].sum()
st.bar_chart(fuel_profit)

# --------------------------------------------------
# MONTHLY PROFIT
# --------------------------------------------------
st.subheader("📊 Monthly Profit Analysis")

monthly_profit = (
    filtered_df
    .groupby("month_name")["profit"]
    .sum()
    .reindex(available_months)
)

st.bar_chart(monthly_profit)

# --------------------------------------------------
# RAW DATA VIEW
# --------------------------------------------------
st.markdown("---")
with st.expander("📄 View Financial Data"):
    st.dataframe(
        filtered_df.sort_values("date"),
        use_container_width=True
    )

# --------------------------------------------------
# EXPLANATION SECTION
# --------------------------------------------------
with st.expander("ℹ️ How profit is calculated"):
    st.write("""
    **Profit Formula:**

    (Selling Price − Buying Price) × Quantity Sold − Expenses

    This represents **actual business operational profit**.
    """)
