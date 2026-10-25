"""NBER recession-period shading, shared behind every chart on the
dashboard. Kept as its own small module (like nowcasts.py) rather than in
loader.py since every page's chart renderer needs it, not just one
section's data.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.config.series import RECESSION_INDICATOR
from dashboard.config.settings import CACHE_TTL_SECONDS
from dashboard.data.fred_client import safe_fetch_series

START = "1990-01-01"


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_recession_periods() -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """NBER recession periods (FRED USREC, trough method) as (start, end)
    date pairs, for shading behind every chart. `end` is the first day of
    the month after the last recession month, so a shaded band covers that
    month's full width rather than stopping at its first day.
    """
    series, _ = safe_fetch_series(RECESSION_INDICATOR, START)
    clean = series.dropna()
    if clean.empty:
        return []

    periods: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    start: pd.Timestamp | None = None
    prev_date: pd.Timestamp | None = None
    for date, flag in clean.items():
        in_recession = flag == 1
        if in_recession and start is None:
            start = date
        elif not in_recession and start is not None:
            periods.append((start, prev_date + pd.DateOffset(months=1)))
            start = None
        prev_date = date
    if start is not None:
        periods.append((start, prev_date + pd.DateOffset(months=1)))
    return periods
