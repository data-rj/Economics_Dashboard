"""Non-FRED GDP nowcast sources: Atlanta Fed GDPNow and NY Fed Staff Nowcast.

GDPNow is published by FRED as a regular series, so it goes through the
same cached FRED client as everything else (see config.series.GDPNOW_ID).

The NY Fed Staff Nowcast has no FRED series or JSON API — the Bank
publishes a weekly Excel workbook. We download and parse it defensively
since its internal layout is not a stable contract.
"""
from __future__ import annotations

from io import BytesIO

import pandas as pd
import requests
import streamlit as st

from dashboard.config.series import NY_FED_NOWCAST_URL
from dashboard.config.settings import CACHE_TTL_SECONDS


class NowcastFetchError(RuntimeError):
    pass


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def _download_nyfed_workbook(url: str) -> bytes:
    try:
        resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
    except requests.RequestException as exc:
        raise NowcastFetchError(f"Network error fetching NY Fed Nowcast: {exc}") from exc
    if resp.status_code != 200:
        raise NowcastFetchError(f"NY Fed Nowcast download failed ({resp.status_code})")
    return resp.content


def get_nyfed_nowcast() -> tuple[float | None, str | None, str | None]:
    """Return (latest_nowcast_value, quarter_label, error_message).

    Defensive parse: scans every sheet for a row whose label mentions
    "nowcast" and takes the most recent non-null numeric value on that row,
    paired with its column header (the forecast quarter / release date).
    """
    try:
        raw = _download_nyfed_workbook(NY_FED_NOWCAST_URL)
        xls = pd.ExcelFile(BytesIO(raw))
        for sheet_name in xls.sheet_names:
            sheet = xls.parse(sheet_name, header=None)
            for i in range(len(sheet)):
                row = sheet.iloc[i]
                label = str(row.iloc[0]) if pd.notna(row.iloc[0]) else ""
                if "nowcast" in label.lower():
                    numeric = pd.to_numeric(row.iloc[1:], errors="coerce").dropna()
                    if numeric.empty:
                        continue
                    last_col_idx = numeric.index[-1]
                    value = numeric.iloc[-1]
                    header_row = sheet.iloc[0]
                    col_label = header_row.get(last_col_idx)
                    return float(value), (str(col_label) if pd.notna(col_label) else None), None
        return None, None, "Could not locate a 'Nowcast' row in the NY Fed workbook."
    except NowcastFetchError as exc:
        return None, None, str(exc)
    except Exception as exc:  # openpyxl/parsing surprises — never crash the app
        return None, None, f"Could not parse NY Fed Nowcast file: {exc}"
