"""Formatting helpers for chart legends and KPI tiles.

Design decision: every legend entry embeds the series' most recent value
and period (per the spec), e.g. "Unemployment Rate (U-3) - 4.1% (Aug 2026)".
"""
from __future__ import annotations

import pandas as pd

FREQ_PERIOD_FORMAT = {
    "D": "%b %d, %Y",
    "W": "%b %d, %Y",
    "M": "%b %Y",
    "Q": "Q{q} %Y",
    "A": "%Y",
}


def format_period(date: pd.Timestamp, freq: str) -> str:
    if freq == "Q":
        q = (date.month - 1) // 3 + 1
        return f"Q{q} {date.year}"
    return date.strftime(FREQ_PERIOD_FORMAT.get(freq, "%b %d, %Y"))


def format_value(value: float, unit: str) -> str:
    if pd.isna(value):
        return "n/a"
    if unit == "pct":
        return f"{value:,.1f}%"
    if unit == "pp":
        return f"{value:,.2f}pp"
    if unit == "ratio":
        return f"{value:,.2f}x"
    if unit == "usd_b":
        return f"${value:,.0f}B"
    if unit == "usd_t":
        return f"${value:,.2f}T"
    if unit == "thousands":
        return f"{value:,.0f}K"
    if unit == "index":
        return f"{value:,.1f}"
    return f"{value:,.2f}"


def legend_label(name: str, series: pd.Series, freq: str, unit: str) -> str:
    """Build a legend entry name that embeds the latest value + period."""
    clean = series.dropna()
    if clean.empty:
        return name
    last_date = clean.index[-1]
    last_value = clean.iloc[-1]
    return (
        f"{name} — {format_value(last_value, unit)} "
        f"({format_period(last_date, freq)})"
    )


def latest_value_and_period(series: pd.Series, freq: str) -> tuple[float | None, str | None]:
    clean = series.dropna()
    if clean.empty:
        return None, None
    return clean.iloc[-1], format_period(clean.index[-1], freq)
