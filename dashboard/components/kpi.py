"""KPI 'bubble' callout tiles (e.g. the 4 GDP headline numbers)."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from dashboard.utils.formatting import format_value


def _format_delta(delta: dict) -> str:
    value = delta.get("value")
    if value is None or pd.isna(value):
        return ""
    invert = delta.get("invert", False)
    is_increase = value > 0
    is_decrease = value < 0
    favorable = is_increase if not invert else is_decrease
    if value == 0:
        color, arrow = "gray", "▬"
    else:
        color = "green" if favorable else "red"
        arrow = "▲" if is_increase else "▼"
    formatted = format_value(abs(value), delta.get("unit", "ratio"))
    return f":{color}[{arrow} {formatted}]"


def kpi_row(items: list[dict]) -> None:
    """items: list of {label, value, unit, period, error(optional),
    sub_metrics(optional): [{label, value, unit}, ...],
    delta(optional): {value, unit, invert}}.
    """
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            with st.container(border=True):
                st.caption(item["label"])
                if item.get("error"):
                    st.markdown("**n/a**")
                    st.caption(item["error"])
                else:
                    value_str = format_value(item["value"], item["unit"])
                    st.markdown(f"## {value_str}")
                    delta = item.get("delta")
                    if delta:
                        delta_text = _format_delta(delta)
                        if delta_text:
                            st.markdown(delta_text)
                    st.caption(item.get("period") or "")
                    for sub in item.get("sub_metrics", []):
                        sub_value = sub.get("value")
                        sub_str = format_value(sub_value, sub["unit"]) if sub_value is not None else "n/a"
                        st.caption(f"{sub['label']}: {sub_str}")
