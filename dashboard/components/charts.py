"""Reusable Plotly chart builders shared by every dashboard page.

Design choices (see dataviz skill):
- Fixed categorical color order, never cycled/reassigned.
- Thin (2px) lines, transparent surface so it adapts to the Streamlit theme.
- Unified hover (crosshair) tooltip on every line/area/bar chart.
- Legend entries embed each series' most recent value + period per the spec.
- A few charts below use a second y-axis because the task explicitly calls
  for it (e.g. industrial production vs. capacity utilization, deficit vs.
  debt/GDP). That is a deliberate exception to the usual one-axis rule,
  made only where the user's spec names a "2nd axis" pairing.
"""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from dashboard.config.settings import (
    AXIS_LINE_COLOR,
    CATEGORICAL_ORDER,
    GRID_COLOR,
    ZERO_LINE_COLOR,
)
from dashboard.utils.formatting import format_value, legend_label

BASE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    hovermode="x unified",
    margin=dict(l=10, r=10, t=10, b=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    # Plotly defaults showlegend to False for a single-trace figure — but
    # this dashboard always embeds each series' latest value/period in its
    # legend entry, so the legend must show even with just one series.
    showlegend=True,
    font=dict(size=13),
)


def _axis_style(title: str | None = None, tickformat: str | None = None, color: str | None = None) -> dict:
    style = dict(
        showgrid=True,
        gridcolor=GRID_COLOR,
        zeroline=False,
        showline=True,
        linecolor=AXIS_LINE_COLOR,
        title=dict(text=title) if title else None,
    )
    if tickformat:
        style["tickformat"] = tickformat
    if color:
        style["title"] = dict(text=title, font=dict(color=color)) if title else None
        style["tickfont"] = dict(color=color)
        style["linecolor"] = color
    return style


def _hover_fmt(unit: str) -> str:
    return {
        "pct": "%{y:.1f}%",
        "pp": "%{y:.2f}pp",
        "ratio": "%{y:.2f}x",
        "usd_b": "$%{y:,.0f}B",
        "usd_t": "$%{y:,.2f}T",
        "thousands": "%{y:,.0f}K",
        "index": "%{y:,.1f}",
    }.get(unit, "%{y:,.2f}")


def multi_line_chart(
    series_dict: dict[str, pd.Series],
    freq: str,
    unit: str,
    y_title: str | None = None,
    zero_line: bool = False,
    reference_lines: list[tuple[float, str, str]] | None = None,
) -> go.Figure:
    """reference_lines: optional (value, label, color) threshold lines —
    e.g. labeled bands for a ratio chart. Drawn dashed with an inline
    annotation rather than relying on color alone (status colors are
    reserved and always paired with a label, never color-only).
    """
    fig = go.Figure()
    for i, (label, series) in enumerate(series_dict.items()):
        color = CATEGORICAL_ORDER[i % len(CATEGORICAL_ORDER)]
        clean = series.dropna()
        fig.add_trace(
            go.Scatter(
                x=clean.index,
                y=clean.values,
                mode="lines",
                name=legend_label(label, series, freq, unit),
                line=dict(width=2, color=color),
                hovertemplate=_hover_fmt(unit) + "<extra>" + label + "</extra>",
            )
        )
    if zero_line:
        fig.add_hline(y=0, line_width=1, line_color=ZERO_LINE_COLOR)
    for value, label, color in reference_lines or []:
        fig.add_hline(
            y=value,
            line_width=1.5,
            line_dash="dot",
            line_color=color,
            annotation_text=label,
            annotation_position="top left",
            annotation_font=dict(size=11, color=color),
        )
    fig.update_layout(**BASE_LAYOUT)
    fig.update_xaxes(**_axis_style())
    fig.update_yaxes(**_axis_style(title=y_title))
    return fig


def stacked_bar_chart(
    series_dict: dict[str, pd.Series],
    freq: str,
    unit: str,
    y_title: str | None = None,
    total_line: tuple[str, pd.Series] | None = None,
) -> go.Figure:
    fig = go.Figure()
    for i, (label, series) in enumerate(series_dict.items()):
        color = CATEGORICAL_ORDER[i % len(CATEGORICAL_ORDER)]
        clean = series.dropna()
        fig.add_trace(
            go.Bar(
                x=clean.index,
                y=clean.values,
                name=legend_label(label, series, freq, unit),
                marker=dict(color=color, line=dict(width=1, color="rgba(0,0,0,0)")),
                hovertemplate=_hover_fmt(unit) + "<extra>" + label + "</extra>",
            )
        )
    if total_line is not None:
        total_label, total_series = total_line
        clean_total = total_series.dropna()
        fig.add_trace(
            go.Scatter(
                x=clean_total.index,
                y=clean_total.values,
                mode="lines",
                name=legend_label(total_label, total_series, freq, unit),
                line=dict(width=2, color="#0b0b0b", dash="dot"),
                hovertemplate=_hover_fmt(unit) + "<extra>" + total_label + "</extra>",
            )
        )
    fig.update_layout(barmode="relative", bargap=0.15, **BASE_LAYOUT)
    fig.add_hline(y=0, line_width=1, line_color=ZERO_LINE_COLOR)
    fig.update_xaxes(**_axis_style())
    fig.update_yaxes(**_axis_style(title=y_title))
    return fig


def dual_axis_chart(
    left: tuple[str, pd.Series, str],
    right: tuple[str, pd.Series, str],
    freq: str,
    left_title: str | None = None,
    right_title: str | None = None,
) -> go.Figure:
    """left/right = (label, series, unit). Explicit 2nd-axis chart, used
    only where the dashboard spec calls for it by name.
    """
    left_label, left_series, left_unit = left
    right_label, right_series, right_unit = right
    left_color = CATEGORICAL_ORDER[0]
    right_color = CATEGORICAL_ORDER[1]

    fig = go.Figure()
    clean_left = left_series.dropna()
    fig.add_trace(
        go.Scatter(
            x=clean_left.index,
            y=clean_left.values,
            mode="lines",
            name=legend_label(left_label, left_series, freq, left_unit),
            line=dict(width=2, color=left_color),
            yaxis="y1",
            hovertemplate=_hover_fmt(left_unit) + "<extra>" + left_label + "</extra>",
        )
    )
    clean_right = right_series.dropna()
    fig.add_trace(
        go.Scatter(
            x=clean_right.index,
            y=clean_right.values,
            mode="lines",
            name=legend_label(right_label, right_series, freq, right_unit),
            line=dict(width=2, color=right_color),
            yaxis="y2",
            hovertemplate=_hover_fmt(right_unit) + "<extra>" + right_label + "</extra>",
        )
    )
    fig.update_layout(
        yaxis=_axis_style(title=left_title, color=left_color),
        yaxis2=dict(**_axis_style(title=right_title, color=right_color), overlaying="y", side="right"),
        **BASE_LAYOUT,
    )
    fig.update_xaxes(**_axis_style())
    return fig


def area_chart(
    series_dict: dict[str, pd.Series],
    freq: str,
    unit: str,
    y_title: str | None = None,
    zero_line: bool = True,
) -> go.Figure:
    """Single-axis filled area chart — e.g. a standalone deficit/surplus
    series where a second axis isn't needed.
    """
    fig = go.Figure()
    for i, (label, series) in enumerate(series_dict.items()):
        color = CATEGORICAL_ORDER[i % len(CATEGORICAL_ORDER)]
        clean = series.dropna()
        fig.add_trace(
            go.Scatter(
                x=clean.index,
                y=clean.values,
                mode="lines",
                fill="tozeroy",
                name=legend_label(label, series, freq, unit),
                line=dict(width=1.5, color=color),
                fillcolor=_to_rgba(color, 0.25),
                hovertemplate=_hover_fmt(unit) + "<extra>" + label + "</extra>",
            )
        )
    if zero_line:
        fig.add_hline(y=0, line_width=1, line_color=ZERO_LINE_COLOR)
    fig.update_layout(**BASE_LAYOUT)
    fig.update_xaxes(**_axis_style())
    fig.update_yaxes(**_axis_style(title=y_title))
    return fig


def _to_rgba(hex_color: str, alpha: float) -> str:
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"
