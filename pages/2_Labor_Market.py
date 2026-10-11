import streamlit as st

from dashboard.components.controls import render_line_section, render_stacked_bar_section
from dashboard.components.kpi import kpi_row
from dashboard.config import series as s
from dashboard.config.settings import STATUS
from dashboard.data import loader

st.title("Labor Market")

kpi_row(loader.load_labor_kpis())

st.divider()

data, errors = loader.load_unemployment_rates()
render_line_section(
    "Unemployment Rate: U-3 vs. U-6",
    "unemployment",
    data,
    errors,
    freq="M",
    unit="pct",
    y_title="%",
    sources=[s.UNRATE, s.U6RATE],
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
    sources=[s.PAYEMS],
)

data, errors = loader.load_survey_comparison()
render_line_section(
    "Establishment vs. Household Survey Employment",
    "survey_comparison",
    data,
    errors,
    freq="M",
    unit="thousands",
    description="Monthly change in employment, establishment (payrolls) survey vs. household survey.",
    zero_line=True,
    y_title="Thousands of jobs",
    sources=[s.PAYEMS, s.HOUSEHOLD_EMPLOYMENT],
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
    sources=[s.AVG_HOURLY_EARNINGS],
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
    sources=[s.INITIAL_CLAIMS, s.INITIAL_CLAIMS_4WK_AVG],
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
    sources=[s.JOLTS_OPENINGS, s.JOLTS_QUITS],
)

data, errors = loader.load_labor_tightness_ratio()
render_line_section(
    "Labor Market Tightness: Job Openings per Unemployed Worker",
    "labor_tightness",
    data,
    errors,
    freq="M",
    unit="ratio",
    description="JOLTS Job Openings ÷ Unemployed Persons. Above 1.2 signals a severe labor "
    "shortage; below 0.8 signals deteriorating labor demand.",
    y_title="Openings per unemployed worker",
    sources=[s.JOLTS_OPENINGS, s.UNEMPLOYED_LEVEL],
    reference_lines=[
        (loader.TIGHTNESS_SEVERE_SHORTAGE, "Severe Shortage (1.2)", STATUS["warning"]),
        (loader.TIGHTNESS_DETERIORATION, "Deterioration (0.8)", STATUS["critical"]),
    ],
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
    sources=[s.LFPR_TOTAL, s.LFPR_16_19, s.LFPR_25_54, s.LFPR_55_PLUS],
)
