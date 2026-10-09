import streamlit as st

from dashboard.components.controls import render_line_section
from dashboard.config import series as s
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
    sources=[s.REAL_PCE, s.REAL_DPI, s.PERSONAL_SAVINGS_RATE],
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
    sources=[s.RETAIL_SALES, s.RETAIL_SALES_EX_AUTOS, s.PCE_SERVICES_REAL],
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
    sources=[s.HH_DSR_TOTAL, s.HH_DSR_MORTGAGE, s.HH_DSR_NON_MORTGAGE],
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
    sources=[s.DELINQ_CONSUMER_BROAD, s.DELINQ_MORTGAGE, s.DELINQ_CREDIT_CARD],
)
