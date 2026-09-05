"""Entry point for the U.S. Economic Dashboard Streamlit app."""
from __future__ import annotations

import streamlit as st

from dashboard.config.settings import APP_TITLE
from dashboard.data.fred_client import has_api_key

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
                "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html. "
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
    st.sidebar.caption(
        "Each chart defaults to 5 years of history — use the range control "
        "above a chart to expand to Max or shrink to 1 year."
    )


def home() -> None:
    st.title(APP_TITLE)
    st.markdown(
        """
Use the navigation in the sidebar to explore each section:

- **Economic Overview** — GDP growth, GDP nowcasts, and the output gap
- **Labor Market** — unemployment, payrolls, wages, claims, JOLTS, participation
- **The Consumer** — spending, income, retail sales, household debt & delinquencies
- **Corporate America** — profits, industrial production, credit spreads, business credit health
- **Public & Private Investment** — fixed investment, housing, business inventories
- **Government** — government spending, federal receipts/outlays, the deficit & debt
- **Prices & Monetary Policy** — inflation, interest rates, money supply, the Fed's balance sheet

All charts default to **5 years** of history and can be expanded to the full
available history or narrowed to the trailing year. Every legend entry shows
each series' most recent value and period.
        """
    )


render_sidebar()

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

nav = st.navigation(
    [home_page, overview, labor, consumer, corporate, investment, government, prices]
)
nav.run()
