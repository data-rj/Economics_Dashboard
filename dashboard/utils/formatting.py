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


def quarter_end_month_label(date: pd.Timestamp) -> str:
    """Month/year label for the END of the quarter `date` falls in.

    FRED indexes quarterly series by the FIRST day of the quarter (e.g.
    2025-07-01 for Q3 2025), so a plain strftime shows "Jul 2025" for data
    that actually describes the quarter ending in September. This shifts
    to the quarter's last month before formatting.
    """
    return date.to_period("Q").end_time.strftime("%b %Y")


def _sign(value: float) -> str:
    """Leading minus for currency, so a deficit reads -$4,608B, not $-4,608B."""
    return "-" if value < 0 else ""


def format_value(value: float, unit: str) -> str:
    if pd.isna(value):
        return "n/a"
    if unit == "pct":
        return f"{value:,.1f}%"
    if unit == "rate":  # market rates/yields/spreads, where the 2nd decimal matters
        return f"{value:,.2f}%"
    if unit == "pp":
        return f"{value:,.2f}pp"
    if unit == "ratio":
        return f"{value:,.2f}x"
    if unit == "usd_b":
        return f"{_sign(value)}${abs(value):,.0f}B"
    if unit == "usd_t":
        return f"{_sign(value)}${abs(value):,.2f}T"
    if unit == "thousands":
        return f"{value:,.0f}K"
    if unit == "index":
        return f"{value:,.1f}"
    return f"{value:,.2f}"


def format_change(value: float, unit: str) -> str:
    """Magnitude of a period-over-period change. A change in a percentage
    is in percentage points, not percent.
    """
    magnitude = abs(value)
    if unit == "pct":
        return f"{magnitude:,.1f}pp"
    if unit == "rate":
        return f"{magnitude:,.2f}pp"
    return format_value(magnitude, unit)


def kpi_period_label(date: pd.Timestamp, freq: str) -> str:
    """KPI-tile period label: quarterly series use the quarter-END month
    (see quarter_end_month_label) rather than format_period's "Q3 2025".
    """
    return quarter_end_month_label(date) if freq == "Q" else format_period(date, freq)


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
    """Latest non-null value + its KPI-tile period label."""
    clean = series.dropna()
    if clean.empty:
        return None, None
    return clean.iloc[-1], kpi_period_label(clean.index[-1], freq)
