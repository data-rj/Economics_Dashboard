import streamlit as st

from dashboard.components.controls import render_dual_axis_section, render_line_section
from dashboard.config import series as s
from dashboard.data import loader

st.title("Corporate America")

data, errors = loader.load_corporate_profits_yoy()
render_line_section(
    "Corporate Profits YoY%",
    "corp_profits_yoy",
    data,
    errors,
    freq="Q",
    unit="pct",
    zero_line=True,
    y_title="YoY % change",
    sources=[s.CORPORATE_PROFITS],
)

data, errors = loader.load_corporate_profits_share_gdp()
render_line_section(
    "Corporate Profits as a Share of GDP",
    "corp_profits_gdp",
    data,
    errors,
    freq="Q",
    unit="pct",
    y_title="% of GDP",
    sources=[s.CORPORATE_PROFITS, s.GDP_NOMINAL],
)

data, errors = loader.load_industrial_production()
render_dual_axis_section(
    "Industrial Production & Capacity Utilization",
    "indpro",
    data,
    errors,
    freq="M",
    left_title="Industrial Production, YoY %",
    right_title="Capacity Utilization, %",
    sources=[s.INDUSTRIAL_PRODUCTION, s.CAPACITY_UTILIZATION],
)

data, errors = loader.load_bond_spreads()
render_line_section(
    "Corporate Bond Spreads by Rating",
    "bond_spreads",
    data,
    errors,
    freq="D",
    unit="pct",
    description="Option-adjusted spread over Treasuries.",
    y_title="Spread (%)",
    sources=[s.BOND_SPREAD_BBB, s.BOND_SPREAD_BB, s.BOND_SPREAD_B, s.BOND_SPREAD_CCC],
)

data, errors = loader.load_corporate_delinquency_chargeoff()
render_line_section(
    "Corporate Delinquencies & Charge-Offs",
    "corp_credit_health",
    data,
    errors,
    freq="Q",
    unit="pct",
    description="Business loans, commercial banks.",
    y_title="%",
    sources=[s.BUSINESS_LOAN_DELINQ, s.BUSINESS_LOAN_CHARGEOFF],
)
