"""KPI callout tiles (e.g. the 4 GDP headline numbers).

Rendered as one CSS grid rather than st.columns so every tile in a row is
the same height and the label / value / change / detail lines sit on the
same baselines across tiles, whatever each tile happens to contain.
"""
from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from dashboard.config.settings import STATUS
from dashboard.utils.formatting import format_change, format_value

_PRIOR_PERIOD = {"D": "prior day", "W": "prior week", "M": "prior month", "Q": "prior quarter", "A": "prior year"}
_NEUTRAL = "rgba(128,128,128,0.9)"
_STATUS_DOT = {"good": STATUS["good"], "warning": STATUS["warning"], "critical": STATUS["critical"]}

_CSS = """<style>
.kpi-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));column-gap:.75rem;row-gap:.75rem;margin-bottom:1rem}
.kpi-tile{display:grid;grid-template-rows:subgrid;grid-row:span 4;row-gap:.2rem;border:1px solid rgba(128,128,128,.3);border-radius:.5rem;padding:.8rem .95rem}
.kpi-label{font-size:.85rem;line-height:1.3;opacity:.7}
.kpi-value{font-size:1.9rem;font-weight:600;line-height:1.15}
.kpi-change{font-size:.85rem;line-height:1.35}
.kpi-detail{font-size:.8rem;line-height:1.45;opacity:.65}
.kpi-muted{opacity:.7}
</style>"""


def _change_html(delta: dict | None) -> str:
    """Change since the previous observation. The arrow carries direction;
    it is only colored where a tile declares which direction is favorable,
    and the wording never relies on that color.
    """
    if not delta:
        return ""
    value = delta.get("value")
    if value is None or pd.isna(value):
        return ""
    unit = delta.get("unit", "ratio")
    versus = _PRIOR_PERIOD.get(delta.get("freq"), "prior period")
    magnitude = format_change(value, unit)
    if magnitude == format_change(0, unit):
        return f'<span class="kpi-muted">▬ unchanged vs {versus}</span>'
    arrow = "▲" if value > 0 else "▼"
    favorable = delta.get("favorable")
    color = _NEUTRAL
    if favorable in ("up", "down"):
        is_good = (value > 0) == (favorable == "up")
        color = STATUS["good"] if is_good else STATUS["critical"]
    return (
        f'<span style="color:{color}">{arrow}</span> {escape(magnitude)} '
        f'<span class="kpi-muted">vs {versus}</span>'
    )


def _status_html(status: dict | None) -> str:
    if not status:
        return ""
    color = _STATUS_DOT.get(status.get("level"), _NEUTRAL)
    return f'<div><span style="color:{color}">●</span> {escape(status["text"])}</div>'


def _tile_html(item: dict) -> str:
    label = f'<div class="kpi-label">{escape(item["label"])}</div>'
    if item.get("error"):
        detail = escape(str(item["error"]), quote=True)
        return (
            f'<div class="kpi-tile">{label}<div class="kpi-value kpi-muted">—</div>'
            f'<div class="kpi-change"><span title="{detail}">Data unavailable ⓘ</span></div>'
            f'<div class="kpi-detail"></div></div>'
        )
    value = escape(format_value(item["value"], item["unit"]))
    change = _change_html(item.get("delta")) + _status_html(item.get("status"))
    details = [escape(item.get("period") or "")]
    for sub in item.get("sub_metrics", []):
        sub_value = sub.get("value")
        sub_text = format_value(sub_value, sub["unit"]) if sub_value is not None else "n/a"
        # Only present when the sub-metric is for a different period than
        # the headline figure, e.g. a YoY rate that can't be computed yet
        # for the latest month while the 3-month trend can.
        as_of = f' ({sub["period"]})' if sub.get("period") else ""
        details.append(escape(f'{sub["label"]}: {sub_text}{as_of}'))
    detail_html = "".join(f"<div>{line}</div>" for line in details if line)
    return (
        f'<div class="kpi-tile">{label}<div class="kpi-value">{value}</div>'
        f'<div class="kpi-change">{change}</div><div class="kpi-detail">{detail_html}</div></div>'
    )


def kpi_row(items: list[dict]) -> None:
    """items: list of {label, value, unit, period, error(optional),
    sub_metrics(optional): [{label, value, unit, period(optional)}, ...],
    delta(optional): {value, unit, freq, favorable("up"/"down"/None)},
    status(optional): {text, level("good"/"warning"/"critical"/None)} — a
    qualitative tag (e.g. "Severe Shortage") for series with a known
    interpretive threshold}.
    """
    tiles = "".join(_tile_html(item) for item in items)
    st.markdown(f'{_CSS}<div class="kpi-grid">{tiles}</div>', unsafe_allow_html=True)
