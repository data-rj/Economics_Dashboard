import streamlit as st

from dashboard.components.controls import render_area_section, render_dual_axis_section, render_line_section
from dashboard.components.kpi import kpi_row
from dashboard.config import series as s
from dashboard.data import loader

st.title("Government")

kpi_row(loader.load_government_kpis())

st.divider()

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

data, errors = loader.load_federal_deficit()
render_area_section(
    "Federal Deficit (TTM)",
    "fed_deficit",
    data,
    errors,
    freq="M",
    unit="usd_b",
    y_title="$ Billions (TTM)",
    sources=[s.FEDERAL_DEFICIT_MONTHLY],
)

data, errors = loader.load_federal_debt_metrics()
render_dual_axis_section(
    "Publicly Held Federal Debt: % of GDP vs. % of US Wealth",
    "fed_debt_metrics",
    data,
    errors,
    freq="Q",
    description="Debt held by the public (excludes intragovernmental holdings) relative to two "
    "different denominators.",
    left_title="Debt, % of GDP",
    right_title="Debt, % of US Household Net Worth",
    sources=[s.FEDERAL_DEBT_PUBLIC_PCT_GDP, s.FEDERAL_DEBT_PUBLIC_LEVEL, s.HOUSEHOLD_NET_WORTH],
)
