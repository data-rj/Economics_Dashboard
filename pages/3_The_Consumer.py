import streamlit as st

from dashboard.components.controls import render_line_section
from dashboard.data import loader

st.title("The Consumer")

data, errors = loader.load_pce_income_savings()
render_line_section(
    "Real PCE, Real Disposable Income & Savings Rate",
    "pce_income",
    data,
    errors,
    freq="M",
    unit="pct",
    zero_line=True,
    y_title="%",
)

data, errors = loader.load_retail_sales()
render_line_section(
    "Retail Sales",
    "retail_sales",
    data,
    errors,
    freq="M",
    unit="pct",
    description="Year-over-year % change.",
    zero_line=True,
    y_title="YoY % change",
)

data, errors = loader.load_household_dsr()
render_line_section(
    "Household Debt Service Ratio",
    "dsr",
    data,
    errors,
    freq="Q",
    unit="pct",
    y_title="% of disposable income",
)

data, errors = loader.load_delinquencies()
render_line_section(
    "Consumer Debt Delinquency Rates",
    "delinquencies",
    data,
    errors,
    freq="Q",
    unit="pct",
    y_title="% delinquent",
)
