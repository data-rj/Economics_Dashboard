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
from dashboard.utils.daterange import clip_to_range, range_control
from dashboard.utils.transforms import to_quarter_end


def chart_header(title: str, key: str, description: str | None = None) -> str:
    left, right = st.columns([4, 1])
    with left:
        st.subheader(title)
        if description:
            st.caption(description)
    with right:
        range_label = range_control(key)
    return range_label


def clip_series_dict(
    series_dict: dict[str, pd.Series], range_label: str, freq: str | None = None
) -> dict[str, pd.Series]:
    clipped = {label: clip_to_range(s, range_label) for label, s in series_dict.items()}
    if freq == "Q":
        clipped = {label: to_quarter_end(s) for label, s in clipped.items()}
    return clipped


def _clip_series(series: pd.Series, range_label: str, freq: str | None = None) -> pd.Series:
    clipped = clip_to_range(series, range_label)
    return to_quarter_end(clipped) if freq == "Q" else clipped


def show_data_errors(errors: dict[str, str]) -> None:
    errors = {k: v for k, v in errors.items() if v}
    if errors:
        with st.expander(f"⚠️ {len(errors)} data source issue(s)", expanded=False):
            for label, err in errors.items():
                st.caption(f"**{label}**: {err}")


def show_source_caption(sources: list[str] | str | None) -> None:
    if not sources:
        return
    text = sources if isinstance(sources, str) else fred_source_caption(sources)
    st.caption(text)


def render_line_section(
    title: str,
    key: str,
    data: dict[str, pd.Series],
    errors: dict[str, str],
    freq: str,
    unit: str,
    description: str | None = None,
    zero_line: bool = False,
    y_title: str | None = None,
    sources: list[str] | str | None = None,
    reference_lines: list[tuple[float, str, str]] | None = None,
) -> None:
    with st.container(border=True):
        range_label = chart_header(title, key, description)
        clipped = clip_series_dict(data, range_label, freq)
        if any(not series.dropna().empty for series in clipped.values()):
            fig = multi_line_chart(
                clipped, freq, unit, y_title=y_title, zero_line=zero_line, reference_lines=reference_lines
            )
            st.plotly_chart(fig, use_container_width=True, key=f"fig_{key}")
        else:
            st.info("No data available.")
        show_source_caption(sources)
        show_data_errors(errors)


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
) -> None:
    with st.container(border=True):
        range_label = chart_header(title, key, description)
        clipped = clip_series_dict(data, range_label, freq)
        clipped_total = None
        if total_line is not None:
            label, series = total_line
            clipped_total = (label, _clip_series(series, range_label, freq))
        if any(not series.dropna().empty for series in clipped.values()):
            fig = stacked_bar_chart(clipped, freq, unit, y_title=y_title, total_line=clipped_total)
            st.plotly_chart(fig, use_container_width=True, key=f"fig_{key}")
        else:
            st.info("No data available.")
        show_source_caption(sources)
        show_data_errors(errors)


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
) -> None:
    with st.container(border=True):
        range_label = chart_header(title, key, description)
        left_label, left_series, left_unit = data["left"]
        right_label, right_series, right_unit = data["right"]
        left_clipped = (left_label, _clip_series(left_series, range_label, freq), left_unit)
        right_clipped = (right_label, _clip_series(right_series, range_label, freq), right_unit)
        if not left_series.dropna().empty or not right_series.dropna().empty:
            fig = dual_axis_chart(
                left_clipped, right_clipped, freq, left_title=left_title, right_title=right_title
            )
            st.plotly_chart(fig, use_container_width=True, key=f"fig_{key}")
        else:
            st.info("No data available.")
        show_source_caption(sources)
        show_data_errors(errors)


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
    with st.container(border=True):
        range_label = chart_header(title, key, description)
        clipped = clip_series_dict(data, range_label, freq)
        if any(not series.dropna().empty for series in clipped.values()):
            fig = area_chart(clipped, freq, unit, y_title=y_title, zero_line=zero_line)
            st.plotly_chart(fig, use_container_width=True, key=f"fig_{key}")
        else:
            st.info("No data available.")
        show_source_caption(sources)
        show_data_errors(errors)
