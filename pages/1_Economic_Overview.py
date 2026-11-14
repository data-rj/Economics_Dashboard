import streamlit as st

from dashboard.components.controls import ChartGrid, render_line_section, render_stacked_bar_section
from dashboard.components.kpi import kpi_row
from dashboard.config import series as s
from dashboard.data import loader
from dashboard.utils.transforms import net_total

st.title("Economic Overview")

kpi_row(loader.load_gdp_kpis())

st.divider()

grid = ChartGrid()

with grid.cell():
    data, errors = loader.load_gdp_growth_lines()
    render_line_section(
        "Real GDP Growth",
        "gdp_growth",
        data,
        errors,
        freq="Q",
        unit="pct",
        description="Year-over-year and quarterly annualized real GDP growth.",
        zero_line=True,
        y_title="% change",
        sources=[s.REAL_GDP, s.GDP_QOQ_ANNUALIZED],
    )

with grid.cell():
    data, errors = loader.load_gdp_actual_vs_potential()
    render_line_section(
        "Real GDP: Actual vs. Potential (CBO)",
        "gdp_vs_potential",
        data,
        errors,
        freq="Q",
        unit="pct",
        description="Year-over-year growth. Potential GDP excludes CBO forecast periods.",
        zero_line=True,
        y_title="YoY % change",
        sources=[s.REAL_GDP, s.GDP_POTENTIAL],
    )

with grid.cell(full_width=True):
    data, errors = loader.load_gdp_contributions()
    render_stacked_bar_section(
        "GDP Growth Contribution by Component",
        "gdp_contrib",
        data,
        errors,
        freq="Q",
        unit="pp",
        description="Contribution to quarterly annualized real GDP growth, percentage points. "
        "The dotted line is their sum — total real GDP growth.",
        y_title="Percentage points",
        total_line=("Total: Real GDP Growth", net_total(data.values())),
        sources=[
            s.GDP_CONTRIB_PCE,
            s.GDP_CONTRIB_INVESTMENT,
            s.GDP_CONTRIB_NET_EXPORTS,
            s.GDP_CONTRIB_GOVERNMENT,
        ],
    )
