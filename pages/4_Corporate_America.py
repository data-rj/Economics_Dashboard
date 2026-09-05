import streamlit as st

from dashboard.components.controls import render_dual_axis_section, render_line_section
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
)
