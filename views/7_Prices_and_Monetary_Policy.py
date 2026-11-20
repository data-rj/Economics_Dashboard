import streamlit as st

from dashboard.components.controls import ChartGrid, render_line_section
from dashboard.components.kpi import kpi_row
from dashboard.config import series as s
from dashboard.config.settings import STATUS
from dashboard.data import loader

st.title("Prices & Monetary Policy")

kpi_row(loader.load_prices_kpis())

st.divider()

grid = ChartGrid()

with grid.cell():
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

with grid.cell():
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

with grid.cell():
    data, errors = loader.load_breakeven_inflation()
    render_line_section(
        "Breakeven Inflation Rates",
        "breakeven_inflation",
        data,
        errors,
        freq="D",
        unit="rate",
        description="Market-implied inflation expectations, derived from Treasury vs. TIPS yields.",
        y_title="%",
        sources=[s.BREAKEVEN_5Y, s.BREAKEVEN_10Y],
    )

with grid.cell():
    data, errors = loader.load_interest_rates()
    render_line_section(
        "Interest Rates",
        "rates",
        data,
        errors,
        freq="W",
        unit="rate",
        zero_line="auto",
        y_title="%",
        sources=[s.FED_FUNDS_RATE_DAILY, s.TREASURY_10Y, s.TREASURY_10Y_2Y_SPREAD],
    )

with grid.cell():
    data, errors = loader.load_monetary_impulse()
    render_line_section(
        "Monetary Impulse vs. Core PCE Inflation",
        "monetary_impulse",
        data,
        errors,
        freq="Q",
        unit="pct",
        description="Impulse: 200 × ln[(M2 × Velocity) ÷ (M2 × Velocity) two quarters earlier], "
        "using quarterly-average M2. Core PCE: 6-month change to each quarter-end month, "
        "annualized the same way. Quarterly, shown only where both are published.",
        zero_line="auto",
        y_title="Annualized %",
        sources=[s.M2_MONEY_SUPPLY, s.M2_VELOCITY, s.CORE_PCE_DEFLATOR],
        reference_lines=[
            (loader.IMPULSE_INFLATIONARY_BREAKOUT, "Inflationary Breakout (7.5%)", STATUS["critical"]),
            (loader.IMPULSE_DEFLATIONARY_COOLING, "Deflationary Cooling (1.5%)", STATUS["warning"]),
        ],
        clip_outliers=True,
    )

with grid.cell():
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
