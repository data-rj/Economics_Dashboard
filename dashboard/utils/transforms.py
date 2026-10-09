"""Common time-series transforms used across the dashboard.

All functions take/return pandas Series indexed by a DatetimeIndex.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

PERIODS_PER_YEAR = {"D": 365, "W": 52, "M": 12, "Q": 4, "A": 1}


def yoy_pct(series: pd.Series, freq: str) -> pd.Series:
    """Year-over-year percent change, frequency-aware (M=12, Q=4, W=52)."""
    periods = PERIODS_PER_YEAR[freq]
    return (series / series.shift(periods) - 1) * 100


def period_annualized_pct(series: pd.Series, freq: str) -> pd.Series:
    """Annualize a single period's growth rate (QoQ or MoM) using a
    geometric compounding convention, e.g. quarterly annualized rate:
    ((x_t / x_{t-1}) ** 4 - 1) * 100.
    """
    periods = PERIODS_PER_YEAR[freq]
    return ((series / series.shift(1)) ** periods - 1) * 100

def diff(series: pd.Series, periods: int = 1) -> pd.Series:
    return series.diff(periods)


def moving_average(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def trailing_sum(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).sum()


def resample_mean(series: pd.Series, rule: str) -> pd.Series:
    """Downsample (e.g. daily -> weekly) by averaging within each bucket."""
    if series.empty:
        return series
    return series.resample(rule).mean()


def ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    aligned_num, aligned_den = numerator.align(denominator, join="inner")
    return aligned_num / aligned_den


def pct_of(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return ratio(numerator, denominator) * 100


def drop_future(series: pd.Series, as_of: pd.Timestamp | None = None) -> pd.Series:
    """Truncate a series to remove any datapoints beyond `as_of` (default:
    today). Used for CBO Potential GDP, which is published with a forecast
    horizon extending years into the future.
    """
    if series.empty:
        return series
    cutoff = as_of if as_of is not None else pd.Timestamp.today().normalize()
    return series[series.index <= cutoff]


def align_frames(series_dict: dict[str, pd.Series]) -> pd.DataFrame:
    """Outer-join a dict of Series into one DataFrame on the date index."""
    return pd.DataFrame(series_dict)
