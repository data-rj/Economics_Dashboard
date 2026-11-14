"""Entry point for the U.S. Economic Dashboard Streamlit app."""
from __future__ import annotations

import time

import streamlit as st

from dashboard.components.kpi import kpi_row
from dashboard.config.settings import APP_TITLE, CACHE_TTL_SECONDS
from dashboard.data import loader
from dashboard.data.fred_client import clear_cached_data, has_api_key, last_fetch_time
from dashboard.utils.daterange import global_range_control

FRED_KEY_URL = "https://fred.stlouisfed.org/docs/api/api_key.html"

st.set_page_config(page_title=APP_TITLE, page_icon="📊", layout="wide")


def render_sidebar() -> None:
    st.sidebar.title(APP_TITLE)
    st.sidebar.caption(
        "Data from FRED (Federal Reserve Bank of St. Louis), the Atlanta Fed, "
        "and the New York Fed."
    )
    if not has_api_key():
        st.sidebar.warning("No FRED API key found.")
        key = st.sidebar.text_input(
            "FRED API key",
            type="password",
            help=(
                f"Get a free key at {FRED_KEY_URL}. "
                "Stored only for this browser session — never written to disk."
            ),
            key="fred_api_key_input",
        )
        if key:
            st.session_state["fred_api_key_override"] = key
            st.rerun()
    else:
        st.sidebar.success("FRED API key configured.")
    st.sidebar.divider()
    global_range_control()
    st.sidebar.caption(
        "Charts default to 5 years of history. Each chart also has its own range buttons."
    )


def render_data_status() -> None:
    """Rendered after the page has run, so it reflects this run's requests."""
    st.sidebar.divider()
    fetched = last_fetch_time()
    if fetched is None:
        status = "No data loaded yet."
    else:
        minutes = int((time.time() - fetched) // 60)
        age = "just now" if minutes < 1 else f"{minutes} min ago"
        status = f"Last request to FRED: {age}. Data is cached for up to {CACHE_TTL_SECONDS // 60} min."
    st.sidebar.caption(status)
    st.sidebar.button(
        "Refresh data",
        on_click=clear_cached_data,
        help="Discard cached data and request everything again.",
    )


def render_missing_key_notice() -> None:
    st.title(APP_TITLE)
    st.info(
        "This dashboard needs a FRED API key to load its data. Paste one into the "
        f"sidebar, or set the `FRED_API_KEY` environment variable. Keys are free: {FRED_KEY_URL}"
    )


def home() -> None:
    st.title(APP_TITLE)
    st.caption("The headline numbers from each section. Open a section for its charts.")
    for page, load_kpis in SECTIONS:
        st.markdown(f"#### {page.icon} {page.title}")
        kpi_row(load_kpis())
        st.page_link(page, label=f"Open {page.title} charts", icon=":material/arrow_forward:")


overview = st.Page(
    "pages/1_Economic_Overview.py", title="Economic Overview", icon="📈", url_path="economic-overview"
)
labor = st.Page("pages/2_Labor_Market.py", title="Labor Market", icon="👷", url_path="labor-market")
consumer = st.Page("pages/3_The_Consumer.py", title="The Consumer", icon="🛍️", url_path="the-consumer")
corporate = st.Page(
    "pages/4_Corporate_America.py", title="Corporate America", icon="🏢", url_path="corporate-america"
)
investment = st.Page(
    "pages/5_Public_and_Private_Investment.py",
    title="Public & Private Investment",
    icon="🏗️",
    url_path="investment",
)
government = st.Page("pages/6_Government.py", title="Government", icon="🏛️", url_path="government")
prices = st.Page(
    "pages/7_Prices_and_Monetary_Policy.py",
    title="Prices & Monetary Policy",
    icon="💵",
    url_path="prices-monetary-policy",
)
home_page = st.Page(home, title="Home", icon="🏠", url_path="", default=True)

SECTIONS = [
    (overview, loader.load_gdp_kpis),
    (labor, loader.load_labor_kpis),
    (consumer, loader.load_consumer_kpis),
    (corporate, loader.load_corporate_kpis),
    (investment, loader.load_investment_kpis),
    (government, loader.load_government_kpis),
    (prices, loader.load_prices_kpis),
]

render_sidebar()
nav = st.navigation(
    [home_page, overview, labor, consumer, corporate, investment, government, prices]
)
# Without a key every tile and chart would show the same error; say it once.
if has_api_key():
    nav.run()
else:
    render_missing_key_notice()
render_data_status()
