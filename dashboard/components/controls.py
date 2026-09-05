"""Shared chart-section wrapper: title, range control, error surfacing."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.components.charts import (
    area_line_dual_axis_chart,
    dual_axis_chart,
    multi_line_chart,
    stacked_bar_chart,
)
from dashboard.utils.daterange import clip_to_range, range_control


def chart_header(title: str, key: str, description: str | None = None) -> str:
    left, right = st.columns([4, 1])
    with left:
        st.subheader(title)
        if description:
            st.caption(description)
    with right:
        range_label = range_control(key)
    return range_label


def clip_series_dict(series_dict: dict[str, pd.Series], range_label: str) -> dict[str, pd.Series]:
    return {label: clip_to_range(s, range_label) for label, s in series_dict.items()}


def show_data_errors(errors: dict[str, str]) -> None:
    errors = {k: v for k, v in errors.items() if v}
    if errors:
        with st.expander(f"⚠️ {len(errors)} data source issue(s)", expanded=False):
            for label, err in errors.items():
                st.caption(f"**{label}**: {err}")


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
) -> None:
    with st.container(border=True):
        range_label = chart_header(title, key, description)
        clipped = clip_series_dict(data, range_label)
        if any(not series.dropna().empty for series in clipped.values()):
            fig = multi_line_chart(clipped, freq, unit, y_title=y_title, zero_line=zero_line)
            st.plotly_chart(fig, use_container_width=True, key=f"fig_{key}")
        else:
            st.info("No data available.")
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
) -> None:
    with st.container(border=True):
        range_label = chart_header(title, key, description)
        clipped = clip_series_dict(data, range_label)
        clipped_total = None
        if total_line is not None:
            label, series = total_line
            clipped_total = (label, clip_to_range(series, range_label))
        if any(not series.dropna().empty for series in clipped.values()):
            fig = stacked_bar_chart(clipped, freq, unit, y_title=y_title, total_line=clipped_total)
            st.plotly_chart(fig, use_container_width=True, key=f"fig_{key}")
        else:
            st.info("No data available.")
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
) -> None:
    with st.container(border=True):
        range_label = chart_header(title, key, description)
        left_label, left_series, left_unit = data["left"]
        right_label, right_series, right_unit = data["right"]
        left_clipped = (left_label, clip_to_range(left_series, range_label), left_unit)
        right_clipped = (right_label, clip_to_range(right_series, range_label), right_unit)
        if not left_series.dropna().empty or not right_series.dropna().empty:
            fig = dual_axis_chart(
                left_clipped, right_clipped, freq, left_title=left_title, right_title=right_title
            )
            st.plotly_chart(fig, use_container_width=True, key=f"fig_{key}")
        else:
            st.info("No data available.")
        show_data_errors(errors)


def render_area_line_section(
    title: str,
    key: str,
    data: dict,
    errors: dict[str, str],
    freq: str,
    description: str | None = None,
    area_title: str | None = None,
    line_title: str | None = None,
) -> None:
    with st.container(border=True):
        range_label = chart_header(title, key, description)
        area_label, area_series, area_unit = data["area"]
        line_label, line_series, line_unit = data["line"]
        area_clipped = (area_label, clip_to_range(area_series, range_label), area_unit)
        line_clipped = (line_label, clip_to_range(line_series, range_label), line_unit)
        if not area_series.dropna().empty or not line_series.dropna().empty:
            fig = area_line_dual_axis_chart(
                area_clipped, line_clipped, freq, area_title=area_title, line_title=line_title
            )
            st.plotly_chart(fig, use_container_width=True, key=f"fig_{key}")
        else:
            st.info("No data available.")
        show_data_errors(errors)
