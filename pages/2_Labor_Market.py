import streamlit as st

from dashboard.components.controls import render_line_section, render_stacked_bar_section
from dashboard.data import loader

st.title("Labor Market")

data, errors = loader.load_unemployment_rates()
render_line_section(
    "Unemployment Rate: U-3 vs. U-6",
    "unemployment",
    data,
    errors,
    freq="M",
    unit="pct",
    y_title="%",
)

change, avg3, err = loader.load_payrolls_change()
render_stacked_bar_section(
    "Nonfarm Payrolls: Monthly Change",
    "payrolls",
    {"Monthly Change": change},
    {"Monthly Change": err},
    freq="M",
    unit="thousands",
    y_title="Thousands of jobs",
    total_line=("3-Month Moving Average", avg3),
)

data, errors = loader.load_avg_hourly_earnings()
render_line_section(
    "Average Hourly Earnings",
    "ahe",
    data,
    errors,
    freq="M",
    unit="pct",
    description="Year-over-year and monthly annualized growth rate.",
    zero_line=True,
    y_title="% change",
)

data, errors = loader.load_jobless_claims()
render_line_section(
    "Initial Jobless Claims",
    "claims",
    data,
    errors,
    freq="W",
    unit="thousands",
    y_title="Claims (thousands)",
)

data, errors = loader.load_jolts()
render_line_section(
    "JOLTS: Job Openings & Quits",
    "jolts",
    data,
    errors,
    freq="M",
    unit="thousands",
    y_title="Level (thousands)",
)

data, errors = loader.load_lfpr_by_age()
render_line_section(
    "Labor Force Participation Rate by Age",
    "lfpr",
    data,
    errors,
    freq="M",
    unit="pct",
    y_title="%",
)
