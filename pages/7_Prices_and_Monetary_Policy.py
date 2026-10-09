import streamlit as st

from dashboard.components.controls import render_dual_axis_section, render_line_section
from dashboard.components.kpi import kpi_row
from dashboard.config import series as s
from dashboard.data import loader

st.title("Prices & Monetary Policy")

kpi_row(loader.load_prices_kpis())

st.divider()

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
    sources=[s.CPI, s.CORE_CPI, s.TRIMMED_MEAN_CPI],
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
    sources=[s.PCE_DEFLATOR, s.CORE_PCE_DEFLATOR, s.TRIMMED_MEAN_PCE],
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
    sources=[s.BREAKEVEN_5Y, s.BREAKEVEN_10Y],
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
    sources=[s.FED_FUNDS_RATE_DAILY, s.TREASURY_10Y, s.TREASURY_10Y_2Y_SPREAD],
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
    sources=[s.M2_MONEY_SUPPLY, s.M2_VELOCITY],
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
    sources=[s.FED_TOTAL_ASSETS],
)
