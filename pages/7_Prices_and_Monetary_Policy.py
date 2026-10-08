import streamlit as st

from dashboard.components.controls import render_dual_axis_section, render_line_section
from dashboard.data import loader

st.title("Prices & Monetary Policy")

data, errors = loader.load_cpi()
render_line_section(
    "CPI Inflation",
    "cpi",
    data,
    errors,
    freq="M",
    unit="pct",
    description="Year-over-year % change.",
    zero_line=True,
    y_title="YoY % change",
)

data, errors = loader.load_pce_deflator()
render_line_section(
    "PCE Deflator Inflation",
    "pce_deflator",
    data,
    errors,
    freq="M",
    unit="pct",
    description="Year-over-year % change.",
    zero_line=True,
    y_title="YoY % change",
)

data, errors = loader.load_breakeven_inflation()
render_line_section(
    "Breakeven Inflation Rates",
    "breakeven_inflation",
    data,
    errors,
    freq="D",
    unit="pct",
    description="Market-implied inflation expectations, derived from Treasury vs. TIPS yields.",
    zero_line=True,
    y_title="%",
)

data, errors = loader.load_interest_rates()
render_line_section(
    "Interest Rates",
    "rates",
    data,
    errors,
    freq="W",
    unit="pct",
    zero_line=True,
    y_title="%",
)

data, errors = loader.load_m2()
render_dual_axis_section(
    "M2 Money Supply & Velocity",
    "m2",
    data,
    errors,
    freq="M",
    left_title="M2 YoY %",
    right_title="M2 Velocity",
)

data, errors = loader.load_fed_balance_sheet()
render_line_section(
    "Federal Reserve Total Assets",
    "fed_balance_sheet",
    data,
    errors,
    freq="W",
    unit="usd_b",
    y_title="$ Billions",
)
