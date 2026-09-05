"""KPI 'bubble' callout tiles (e.g. the 4 GDP headline numbers)."""
from __future__ import annotations

import streamlit as st

from dashboard.utils.formatting import format_value


def kpi_row(items: list[dict]) -> None:
    """items: list of {label, value, unit, period, error(optional)}."""
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
                    st.caption(item.get("period") or "")
