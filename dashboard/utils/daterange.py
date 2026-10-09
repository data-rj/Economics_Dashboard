"""Per-chart date-range control: defaults to 5 years, expandable to 10Y,
20Y, or max, or shrinkable to 1 year, per the dashboard spec.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

RANGE_OPTIONS = {"1Y": 1, "5Y": 5, "10Y": 10, "20Y": 20, "Max": None}
DEFAULT_RANGE = "5Y"
_RANGE_LABELS = list(RANGE_OPTIONS.keys())


def range_control(key: str) -> str:
    """Render a compact dropdown and return the selected label."""
    return st.selectbox(
        "Range",
        options=_RANGE_LABELS,
        index=_RANGE_LABELS.index(DEFAULT_RANGE),
        key=f"range_{key}",
        label_visibility="collapsed",
    )


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
