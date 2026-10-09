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

import re
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


def _quarter_label(raw: object) -> str:
    """Normalize a column header like "2026Q3" to "Q3 2026"; pass through
    anything that doesn't match that shape unchanged.
    """
    text = str(raw).strip()
    m = re.fullmatch(r"(\d{4})\s*[Qq](\d)", text)
    if m:
        year, q = m.groups()
        return f"Q{q} {year}"
    return text


def _parse_release_dated_sheet(sheet: pd.DataFrame) -> tuple[float, str] | None:
    """Parse the layout the real NY Fed workbook actually uses: column 0 is
    "Forecast Date" with one weekly release date per row (rows 1+), and the
    header row (row 0) labels the other columns by target quarter or
    forecast horizon. Takes the most recent release (last valid date row)
    and the rightmost non-null value on that row — the actively-tracked
    nowcast; older target-quarter columns go stale/NaN once that quarter's
    actual GDP print is out.
    """
    if sheet.shape[0] < 2 or sheet.shape[1] < 2:
        return None

    header_row = sheet.iloc[0]
    dates = pd.to_datetime(sheet.iloc[1:, 0], errors="coerce")
    valid_dates = dates.dropna()
    if valid_dates.empty:
        return None

    row_idx = valid_dates.index[-1]
    row = sheet.loc[row_idx]
    numeric = pd.to_numeric(row.iloc[1:], errors="coerce").dropna()
    if numeric.empty:
        return None

    col_idx = numeric.index[-1]
    value = float(numeric.iloc[-1])
    col_label = header_row.get(col_idx)
    release_date = valid_dates.loc[row_idx]

    label = _quarter_label(col_label) if pd.notna(col_label) else "current quarter"
    return value, f"{label} (as of {release_date.strftime('%b %d, %Y')})"


def get_nyfed_nowcast() -> tuple[float | None, str | None, str | None]:
    """Return (latest_nowcast_value, period_label, error_message).

    The real workbook (confirmed from a live error report, since
    newyorkfed.org is unreachable from this dev environment) is organized
    with release dates down the rows and target quarters / horizons across
    the columns — see _parse_release_dated_sheet. We try that on every
    sheet, preferring ones whose name suggests a quarter/horizon table,
    then fall back to the older "row labeled 'Nowcast'" layout in case the
    file changes shape again. If nothing matches, the error reports every
    sheet's name, shape, and a sample of actual cell values (not just
    column 0) so a further mismatch can be diagnosed without guessing.
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

    sheets: dict[str, pd.DataFrame] = {}
    sheet_samples = []
    for sheet_name in xls.sheet_names:
        try:
            sheets[sheet_name] = xls.parse(sheet_name, header=None)
        except Exception as exc:
            sheet_samples.append(f"'{sheet_name}': <failed to parse: {exc}>")

    # Prefer a sheet named like "... By Quarter" / "... By Horizon" first,
    # since those are the release-dated tables; try the rest after.
    ordered_names = sorted(
        sheets, key=lambda name: ("quarter" not in name.lower() and "horizon" not in name.lower())
    )

    for sheet_name in ordered_names:
        parsed = _parse_release_dated_sheet(sheets[sheet_name])
        if parsed is not None:
            value, period = parsed
            return value, period, None

    # Fallback: older layout — a row whose first-column label mentions
    # "nowcast", with values spread across that row's other columns.
    for sheet_name, sheet in sheets.items():
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

    for sheet_name, sheet in sheets.items():
        preview = sheet.iloc[: min(6, len(sheet)), : min(5, sheet.shape[1])].to_dict(orient="split")["data"]
        sheet_samples.append(f"'{sheet_name}' ({sheet.shape[0]}x{sheet.shape[1]}): {preview}")

    return None, None, (
        "Could not parse the NY Fed workbook with either known layout. "
        "Sheet previews: " + " | ".join(sheet_samples)
    )
