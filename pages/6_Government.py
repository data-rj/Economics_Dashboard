import streamlit as st

from dashboard.components.controls import render_area_line_section, render_line_section
from dashboard.config import series as s
from dashboard.data import loader

st.title("Government")

data, errors = loader.load_gov_consumption_yoy()
render_line_section(
    "Government Consumption & Investment YoY%",
    "gov_consumption",
    data,
    errors,
    freq="Q",
    unit="pct",
    zero_line=True,
    y_title="YoY % change",
    sources=[s.GOV_CONSUMPTION_INVESTMENT_REAL],
)

data, errors = loader.load_federal_outlays_receipts()
render_line_section(
    "Federal Outlays & Receipts",
    "fed_outlays_receipts",
    data,
    errors,
    freq="Q",
    unit="usd_b",
    description="Seasonally adjusted annual rate.",
    y_title="$ Billions (SAAR)",
    sources=[s.FEDERAL_RECEIPTS, s.FEDERAL_OUTLAYS],
)

data, errors = loader.load_federal_deficit_debt()
render_area_line_section(
    "Federal Deficit & Debt",
    "fed_deficit_debt",
    data,
    errors,
    freq="M",
    area_title="Federal Deficit, TTM ($B)",
    line_title="Federal Debt (% of GDP)",
    sources=[s.FEDERAL_DEFICIT_MONTHLY, s.FEDERAL_DEBT_PCT_GDP],
)
