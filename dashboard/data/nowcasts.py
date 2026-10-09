"""Non-FRED GDP nowcast sources: Atlanta Fed GDPNow and NY Fed Staff Nowcast.

GDPNow is published by FRED as a regular series, so it goes through the
same cached FRED client as everything else (see config.series.GDPNOW_ID).

The NY Fed Staff Nowcast has no FRED series or JSON API — the Bank
publishes a weekly Excel workbook. We download and parse it defensively
since its internal layout is not a stable contract, and we were unable to
verify newyorkfed.org's current file structure directly (that domain is
blocked from this dev environment's outbound network). If parsing fails,
the error message below is built to be diagnostic — it reports the sheet
names and sample row labels actually found, so a failure can be debugged
from the error text alone without needing to re-fetch the file.
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
        raise NowcastFetchError(
            f"NY Fed Nowcast download failed ({resp.status_code}) from {url}"
        )
    content_type = resp.headers.get("content-type", "")
    looks_like_excel = (
        "spreadsheet" in content_type
        or "excel" in content_type
        or resp.content[:2] == b"PK"  # xlsx files are zip archives
    )
    if not looks_like_excel:
        raise NowcastFetchError(
            f"NY Fed Nowcast URL did not return an Excel file (content-type: "
            f"'{content_type}', {len(resp.content)} bytes) — the download link "
            f"may have moved. URL tried: {url}"
        )
    return resp.content


def get_nyfed_nowcast() -> tuple[float | None, str | None, str | None]:
    """Return (latest_nowcast_value, quarter_label, error_message).

    Defensive parse: scans every sheet for a row whose label mentions
    "nowcast" and takes the most recent non-null numeric value on that row,
    paired with its column header (the forecast quarter / release date).
    If no such row is found, the error message includes the sheet names
    and sample first-column labels so the real layout can be diagnosed
    without another round trip.
    """
    try:
        raw = _download_nyfed_workbook(NY_FED_NOWCAST_URL)
    except NowcastFetchError as exc:
        return None, None, str(exc)

    try:
        xls = pd.ExcelFile(BytesIO(raw))
    except Exception as exc:
        return None, None, (
            f"Downloaded {len(raw)} bytes from {NY_FED_NOWCAST_URL} but it isn't "
            f"a readable Excel workbook ({exc}). The download link may have moved."
        )

    sheet_samples = []
    for sheet_name in xls.sheet_names:
        try:
            sheet = xls.parse(sheet_name, header=None)
        except Exception as exc:
            sheet_samples.append(f"'{sheet_name}': <failed to parse: {exc}>")
            continue

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

        sample_labels = [
            str(v) for v in sheet.iloc[:15, 0].tolist() if pd.notna(v)
        ][:10]
        sheet_samples.append(f"'{sheet_name}' ({sheet.shape[0]}x{sheet.shape[1]}): {sample_labels}")

    return None, None, (
        "Could not locate a row labeled 'Nowcast' in the NY Fed workbook. "
        "Sheets found: " + " | ".join(sheet_samples)
    )
