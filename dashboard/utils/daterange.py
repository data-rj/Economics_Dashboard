"""Date-range controls: every chart defaults to 5 years and can be switched
to 1Y / 10Y / 20Y / Max with one click, either per chart or for all charts
at once from the sidebar.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

RANGE_OPTIONS = {"1Y": 1, "5Y": 5, "10Y": 10, "20Y": 20, "Max": None}
DEFAULT_RANGE = "5Y"
_RANGE_LABELS = list(RANGE_OPTIONS.keys())

GLOBAL_RANGE_KEY = "global_range"
_CHART_RANGE_PREFIX = "range_"


def default_range() -> str:
    """The sidebar's "all charts" range — what a chart shows until its own
    control is used.
    """
    return st.session_state.get(GLOBAL_RANGE_KEY) or DEFAULT_RANGE


def _reset_chart_ranges() -> None:
    # Dropping each chart's stored choice makes it fall back to its default,
    # which is the sidebar range that just changed.
    for key in [k for k in st.session_state if isinstance(k, str) and k.startswith(_CHART_RANGE_PREFIX)]:
        del st.session_state[key]


def global_range_control() -> None:
    st.sidebar.segmented_control(
        "Range for all charts",
        options=_RANGE_LABELS,
        default=DEFAULT_RANGE,
        key=GLOBAL_RANGE_KEY,
        on_change=_reset_chart_ranges,
        help="Sets every chart to this range. Each chart also has its own range buttons.",
    )


def range_control(key: str) -> str:
    """Render one chart's range buttons and return the selected label."""
    selected = st.segmented_control(
        "Range",
        options=_RANGE_LABELS,
        default=default_range(),
        key=f"{_CHART_RANGE_PREFIX}{key}",
        label_visibility="collapsed",
    )
    return selected or default_range()  # clicking the active button deselects it


def clip_to_range(series: pd.Series, range_label: str) -> pd.Series:
    years = RANGE_OPTIONS.get(range_label)
    if years is None or series.empty:
        return series
    cutoff = series.index.max() - pd.DateOffset(years=years)
    return series[series.index >= cutoff]


def clip_frame_to_range(df: pd.DataFrame, range_label: str) -> pd.DataFrame:
    years = RANGE_OPTIONS.get(range_label)
    if years is None or df.empty:
        return df
    cutoff = df.index.max() - pd.DateOffset(years=years)
    return df[df.index >= cutoff]
