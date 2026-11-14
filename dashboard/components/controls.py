"""Shared chart-section wrapper: title, range control, error surfacing."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.components.charts import (
    area_chart,
    dual_axis_chart,
    multi_line_chart,
    stacked_bar_chart,
)
from dashboard.config.sources import fred_source_caption
from dashboard.data.recessions import load_recession_periods
from dashboard.utils.daterange import clip_to_range, range_control
from dashboard.utils.transforms import to_month_end, to_quarter_end

RECESSION_NOTE = "Shaded areas: NBER recessions."
CLIPPED_NOTE = "Y-axis clipped to the typical range, so extreme values run off-scale — switch on “Full y-range” to see them."


class ChartGrid:
    """Lays chart sections out two to a row on wide screens (Streamlit
    stacks the columns on narrow ones). Usage: `with grid.cell(): ...`.
    """

    def __init__(self, columns: int = 2) -> None:
        self._columns = columns
        self._free: list = []

    def cell(self, full_width: bool = False):
        if full_width:
            self._free = []
            return st.container()
        if not self._free:
            self._free = list(st.columns(self._columns, gap="medium"))
        return self._free.pop(0)


def chart_header(title: str, key: str, description: str | None = None) -> str:
    st.markdown(f"#### {title}")
    if description:
        st.caption(description)
    return range_control(key)


def clip_series_dict(
    series_dict: dict[str, pd.Series], range_label: str, freq: str | None = None
) -> dict[str, pd.Series]:
    clipped = {label: clip_to_range(s, range_label) for label, s in series_dict.items()}
    if freq == "Q":
        clipped = {label: to_quarter_end(s) for label, s in clipped.items()}
    return clipped


def _clip_series(
    series: pd.Series, range_label: str, freq: str | None = None, month_end: bool = False
) -> pd.Series:
    clipped = clip_to_range(series, range_label)
    if freq == "Q":
        return to_quarter_end(clipped)
    if freq == "M" and month_end:
        return to_month_end(clipped)
    return clipped


def _recession_periods_in_range(series_list: list[pd.Series]):
    """Recession periods overlapping the chart's already-clipped date
    range, each trimmed to that range. Plotly's add_vrect shapes count
    toward x-axis autorange, so a band reaching past the data — an
    unfiltered 1990-present list, or one recession that began before the
    chart's first point — would silently widen the x-axis to fit it.
    """
    non_empty = [series.dropna() for series in series_list if not series.dropna().empty]
    if not non_empty:
        return []
    lo = min(series.index.min() for series in non_empty)
    hi = max(series.index.max() for series in non_empty)
    return [
        (max(start, lo), min(end, hi))
        for start, end in load_recession_periods()
        if end > lo and start < hi
    ]


def _typical_y_range(series_list: list[pd.Series], include_zero: bool = False) -> tuple[float, float] | None:
    """A y-range covering the bulk of the data, or None when nothing is
    extreme enough to need one. Bounds are the quartiles +/- 4 IQRs — a
    robust spread that a run of outliers (e.g. the 2020 payroll/claims
    spike, which can be 10% of a 10-year window) can't drag outward the way
    a min/max or a percentile cut would.
    """
    parts = [series.dropna() for series in series_list if not series.dropna().empty]
    if not parts:
        return None
    values = pd.concat(parts)
    if len(values) < 8:
        return None
    q1, q3 = values.quantile(0.25), values.quantile(0.75)
    spread = q3 - q1
    if spread <= 0:
        return None
    lo, hi = q1 - 4 * spread, q3 + 4 * spread
    if values.min() >= lo and values.max() <= hi:
        return None
    lo, hi = max(lo, values.min()), min(hi, values.max())
    if include_zero:
        lo, hi = min(lo, 0), max(hi, 0)
    pad = 0.05 * (hi - lo)
    return lo - pad, hi + pad


def _outlier_y_range(key: str, series_list: list[pd.Series], include_zero: bool = False):
    full_range = st.toggle("Full y-range", key=f"fullrange_{key}")
    return None if full_range else _typical_y_range(series_list, include_zero)


def show_data_errors(errors: dict[str, str]) -> None:
    errors = {k: v for k, v in errors.items() if v}
    if errors:
        with st.expander(f"⚠️ {len(errors)} data source issue(s)", expanded=False):
            for label, err in errors.items():
                st.caption(f"**{label}**: {err}")


def show_source_caption(sources: list[str] | str | None, notes: list[str] | None = None) -> None:
    parts = []
    if sources:
        parts.append(sources if isinstance(sources, str) else fred_source_caption(sources))
    parts.extend(notes or [])
    if parts:
        st.caption(" ".join(parts))


def _chart_notes(recession_periods: list, clipped: bool = False) -> list[str]:
    notes = [RECESSION_NOTE] if recession_periods else []
    if clipped:
        notes.append(CLIPPED_NOTE)
    return notes


# Each section is a fragment: using a chart's own controls re-renders just
# that chart instead of re-running the whole page.
@st.fragment
def render_line_section(
    title: str,
    key: str,
    data: dict[str, pd.Series],
    errors: dict[str, str],
    freq: str,
    unit: str,
    description: str | None = None,
    zero_line: bool | str = False,
    y_title: str | None = None,
    sources: list[str] | str | None = None,
    reference_lines: list[tuple[float, str, str]] | None = None,
    derived: dict[str, str] | None = None,
    clip_outliers: bool = False,
) -> None:
    """derived: see multi_line_chart. clip_outliers: keep the y-axis on the
    typical range (with a toggle to see everything) for a series whose rare
    extremes would otherwise flatten the rest of the line.
    """
    with st.container(border=True, height="stretch"):
        range_label = chart_header(title, key, description)
        clipped = clip_series_dict(data, range_label, freq)
        notes: list[str] = []
        if any(not series.dropna().empty for series in clipped.values()):
            y_range = _outlier_y_range(key, list(clipped.values())) if clip_outliers else None
            recession_periods = _recession_periods_in_range(list(clipped.values()))
            fig = multi_line_chart(
                clipped,
                freq,
                unit,
                y_title=y_title,
                zero_line=zero_line,
                reference_lines=reference_lines,
                recession_periods=recession_periods,
                derived=derived,
                y_range=y_range,
            )
            st.plotly_chart(fig, width="stretch", key=f"fig_{key}")
            notes = _chart_notes(recession_periods, clipped=y_range is not None)
        else:
            st.info("No data available.")
        show_source_caption(sources, notes)
        show_data_errors(errors)


@st.fragment
def render_stacked_bar_section(
    title: str,
    key: str,
    data: dict[str, pd.Series],
    errors: dict[str, str],
    freq: str,
    unit: str,
    description: str | None = None,
    y_title: str | None = None,
    total_line: tuple[str, pd.Series] | None = None,
    sources: list[str] | str | None = None,
    clip_outliers: bool = False,
) -> None:
    with st.container(border=True, height="stretch"):
        range_label = chart_header(title, key, description)
        clipped = clip_series_dict(data, range_label, freq)
        clipped_total = None
        if total_line is not None:
            label, series = total_line
            clipped_total = (label, _clip_series(series, range_label, freq))
        notes: list[str] = []
        if any(not series.dropna().empty for series in clipped.values()):
            plotted = list(clipped.values())
            if clipped_total is not None:
                plotted.append(clipped_total[1])
            y_range = _outlier_y_range(key, plotted, include_zero=True) if clip_outliers else None
            recession_periods = _recession_periods_in_range(plotted)
            fig = stacked_bar_chart(
                clipped,
                freq,
                unit,
                y_title=y_title,
                total_line=clipped_total,
                recession_periods=recession_periods,
                y_range=y_range,
            )
            st.plotly_chart(fig, width="stretch", key=f"fig_{key}")
            notes = _chart_notes(recession_periods, clipped=y_range is not None)
        else:
            st.info("No data available.")
        show_source_caption(sources, notes)
        show_data_errors(errors)


@st.fragment
def render_dual_axis_section(
    title: str,
    key: str,
    data: dict,
    errors: dict[str, str],
    freq: str,
    description: str | None = None,
    left_title: str | None = None,
    right_title: str | None = None,
    sources: list[str] | str | None = None,
    left_freq: str | None = None,
    right_freq: str | None = None,
    left_month_end: bool = False,
    right_month_end: bool = False,
) -> None:
    """left_freq/right_freq: override `freq` for date-range clipping and the
    quarter-end shift on one side only, for a mixed-cadence pairing (e.g.
    M2 YoY% is monthly but M2 Velocity is quarterly). `freq` alone still
    drives the chart's hover/legend period formatting for both sides — a
    quarter-end-shifted date formatted with freq="M" already reads as e.g.
    "Jun 2026", matching the quarter-end convention used on KPI tiles.

    left_month_end/right_month_end: opt a monthly ("M") side into the same
    month-start -> month-end relabeling, for a specific chart that asks for
    it. Unlike the quarter-end shift, this isn't dashboard-wide, so it's an
    explicit per-chart flag rather than automatic for every "M" series.
    """
    with st.container(border=True, height="stretch"):
        range_label = chart_header(title, key, description)
        left_label, left_series, left_unit = data["left"]
        right_label, right_series, right_unit = data["right"]
        left_clipped = (
            left_label,
            _clip_series(left_series, range_label, left_freq or freq, left_month_end),
            left_unit,
        )
        right_clipped = (
            right_label,
            _clip_series(right_series, range_label, right_freq or freq, right_month_end),
            right_unit,
        )
        notes: list[str] = []
        if not left_series.dropna().empty or not right_series.dropna().empty:
            recession_periods = _recession_periods_in_range([left_clipped[1], right_clipped[1]])
            fig = dual_axis_chart(
                left_clipped,
                right_clipped,
                freq,
                left_title=left_title,
                right_title=right_title,
                recession_periods=recession_periods,
            )
            st.plotly_chart(fig, width="stretch", key=f"fig_{key}")
            notes = _chart_notes(recession_periods)
        else:
            st.info("No data available.")
        show_source_caption(sources, notes)
        show_data_errors(errors)


@st.fragment
def render_area_section(
    title: str,
    key: str,
    data: dict[str, pd.Series],
    errors: dict[str, str],
    freq: str,
    unit: str,
    description: str | None = None,
    zero_line: bool = True,
    y_title: str | None = None,
    sources: list[str] | str | None = None,
) -> None:
    with st.container(border=True, height="stretch"):
        range_label = chart_header(title, key, description)
        clipped = clip_series_dict(data, range_label, freq)
        notes: list[str] = []
        if any(not series.dropna().empty for series in clipped.values()):
            recession_periods = _recession_periods_in_range(list(clipped.values()))
            fig = area_chart(
                clipped, freq, unit, y_title=y_title, zero_line=zero_line, recession_periods=recession_periods
            )
            st.plotly_chart(fig, width="stretch", key=f"fig_{key}")
            notes = _chart_notes(recession_periods)
        else:
            st.info("No data available.")
        show_source_caption(sources, notes)
        show_data_errors(errors)
