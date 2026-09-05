"""Thin, cached client for the FRED (St. Louis Fed) REST API.

No third-party FRED SDK is used — a plain `requests` call keeps the
dependency footprint small and gives full control over caching.
"""
from __future__ import annotations

import os

import pandas as pd
import requests
import streamlit as st

from dashboard.config.settings import CACHE_TTL_SECONDS, FRED_BASE_URL


class FredRequestError(RuntimeError):
    """Raised when the FRED API can't be reached or rejects the request."""


def get_api_key() -> str | None:
    """Resolve the FRED API key: user-entered override > st.secrets > env var."""
    override = st.session_state.get("fred_api_key_override")
    if override:
        return override
    try:
        if "FRED_API_KEY" in st.secrets:
            return st.secrets["FRED_API_KEY"]
    except Exception:
        pass
    return os.environ.get("FRED_API_KEY")


def has_api_key() -> bool:
    return bool(get_api_key())


def _redact(text: str, api_key: str) -> str:
    """Strip the API key out of any error text before it can reach the UI."""
    return text.replace(api_key, "***") if api_key else text


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def _fetch_observations(series_id: str, api_key: str, observation_start: str) -> pd.DataFrame:
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": observation_start,
    }
    try:
        resp = requests.get(FRED_BASE_URL, params=params, timeout=20)
    except requests.RequestException as exc:
        raise FredRequestError(_redact(f"Network error fetching {series_id}: {exc}", api_key)) from exc

    if resp.status_code != 200:
        detail = ""
        try:
            detail = resp.json().get("error_message", "")
        except Exception:
            detail = resp.text[:200]
        raise FredRequestError(_redact(f"FRED API error for {series_id} ({resp.status_code}): {detail}", api_key))

    payload = resp.json()
    obs = payload.get("observations", [])
    df = pd.DataFrame(obs)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df[["date", "value"]]


def fetch_series(series_id: str, observation_start: str = "1990-01-01") -> pd.Series:
    """Fetch a FRED series as a pandas Series indexed by date. Raises
    FredRequestError if the API key is missing or the request fails.
    """
    api_key = get_api_key()
    if not api_key:
        raise FredRequestError(
            "No FRED API key configured. Add one in the sidebar or set FRED_API_KEY."
        )
    df = _fetch_observations(series_id, api_key, observation_start)
    if df.empty:
        return pd.Series(dtype=float, name=series_id)
    return df.set_index("date")["value"].rename(series_id).sort_index()


def safe_fetch_series(series_id: str, observation_start: str = "1990-01-01") -> tuple[pd.Series, str | None]:
    """Same as fetch_series but never raises — returns (series, error_message)."""
    try:
        return fetch_series(series_id, observation_start), None
    except FredRequestError as exc:
        return pd.Series(dtype=float, name=series_id), str(exc)
