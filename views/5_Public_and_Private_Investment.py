import streamlit as st

from dashboard.components.controls import (
    ChartGrid,
    render_dual_axis_section,
    render_line_section,
    render_stacked_bar_section,
)
from dashboard.components.kpi import kpi_row
from dashboard.config import series as s
from dashboard.data import loader
from dashboard.utils.transforms import net_total

st.title("Public & Private Investment")

kpi_row(loader.load_investment_kpis())

st.divider()

grid = ChartGrid()

with grid.cell():
    data, errors = loader.load_fixed_investment_yoy()
    render_line_section(
        "Fixed Investment: Nonresidential vs. Residential",
        "fixed_investment",
        data,
        errors,
        freq="Q",
        unit="pct",
        description="Year-over-year % change.",
        zero_line=True,
        y_title="YoY % change",
        sources=[s.NONRESIDENTIAL_FIXED_INVESTMENT_REAL, s.RESIDENTIAL_FIXED_INVESTMENT_REAL],
    )

with grid.cell():
    data, errors = loader.load_investment_contributions()
    render_stacked_bar_section(
        "Nonresidential Fixed Investment: Contribution by Component",
        "investment_contrib",
        data,
        errors,
        freq="Q",
        unit="pp",
        description="Contribution to the quarterly annualized % change in real private fixed "
        "investment, percentage points. The dotted line is their sum — the total nonresidential "
        "contribution.",
        y_title="Percentage points",
        total_line=("Total Nonresidential Contribution", net_total(data.values())),
        sources=[
            s.INVESTMENT_CONTRIB_STRUCTURES,
            s.INVESTMENT_CONTRIB_EQUIPMENT,
            s.INVESTMENT_CONTRIB_IP_PRODUCTS,
        ],
    )

with grid.cell():
    data, errors = loader.load_housing()
    render_line_section(
        "Housing Starts & Building Permits",
        "housing",
        data,
        errors,
        freq="M",
        unit="thousands",
        description="Seasonally adjusted annual rate.",
        y_title="Thousands of units (SAAR)",
        sources=[s.HOUSING_STARTS, s.HOUSING_PERMITS],
    )

with grid.cell():
    data, errors = loader.load_inventory_ratio()
    render_dual_axis_section(
        "Business Inventories & Inventory-to-Sales Ratio",
        "inventory_ratio",
        data,
        errors,
        freq="M",
        left_title="Total Business Inventories, YoY %",
        right_title="Inventory-to-Sales Ratio",
        sources=[s.BUSINESS_INVENTORIES, s.INVENTORY_SALES_RATIO],
    )
