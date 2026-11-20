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


def window_annualized_pct(series: pd.Series, freq: str, window: int) -> pd.Series:
    """Annualize the compounded growth rate over `window` periods, e.g. a
    "3-month annualized" rate: ((x_t / x_{t-3}) ** (12/3) - 1) * 100. This
    is the standard compounding definition (not a moving average of
    already-annualized single-period rates), so it reads consistently
    with period_annualized_pct's 1-period case.
    """
    periods = PERIODS_PER_YEAR[freq]
    return ((series / series.shift(window)) ** (periods / window) - 1) * 100


def log_annualized_pct(series: pd.Series, freq: str, window: int) -> pd.Series:
    """Annualized log change over `window` periods:
    (periods_per_year / window) * 100 * ln(x_t / x_{t-window}) — e.g. 200 *
    ln(x_t / x_{t-2}) for two quarters or six months. Expects a regular
    index (no skipped periods), so shift(window) is `window` periods back.
    """
    periods = PERIODS_PER_YEAR[freq]
    return (periods / window) * 100 * np.log(series / series.shift(window))


def diff(series: pd.Series, periods: int = 1) -> pd.Series:
    return series.diff(periods)


def moving_average(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).mean()


def trailing_time_average(series: pd.Series, window: str) -> pd.Series:
    """Rolling mean over a calendar-time window (e.g. "90D" for ~3 months),
    for irregular-cadence series (daily data with weekend/holiday gaps)
    where moving_average's row-count window wouldn't line up with
    calendar time.
    """
    if series.empty:
        return series
    return series.rolling(window).mean()


def trailing_sum(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=window).sum()


def resample_mean(series: pd.Series, rule: str) -> pd.Series:
    """Downsample (e.g. daily -> weekly) by averaging within each bucket.

    pandas labels each bucket by its END, so the current, still-incomplete
    bucket would be stamped with a date in the future (the coming Sunday for
    "W"). Stamp that last bucket with the last actual observation instead.
    """
    clean = series.dropna()
    if clean.empty:
        return clean
    out = clean.resample(rule).mean()
    last_obs = clean.index[-1]
    if out.index[-1] > last_obs:
        out = out.set_axis(out.index[:-1].append(pd.DatetimeIndex([last_obs])))
    return out


def ratio(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    aligned_num, aligned_den = numerator.align(denominator, join="inner")
    return aligned_num / aligned_den


def pct_of(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return ratio(numerator, denominator) * 100


def to_quarter_end(series: pd.Series) -> pd.Series:
    """Relabel a quarterly series' index from FRED's quarter-START convention
    (e.g. 2025-07-01 for Q3 2025) to the quarter's last calendar day (e.g.
    2025-09-30), for display only. Values and ordering are unchanged, so
    this is safe to apply after any YoY/diff/moving-average math and after
    date-range clipping, right before a chart is built.
    """
    if series.empty:
        return series
    return series.set_axis(series.index.to_period("Q").end_time.normalize())


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


def net_total(series_list) -> pd.Series:
    """Row-wise sum of component series, NaN wherever any component is
    missing — so a "net" line never shows a partial sum as if it were whole.
    """
    return pd.concat(list(series_list), axis=1).sum(axis=1, skipna=False)


def align_to_common_end(*series_list: pd.Series) -> list[pd.Series]:
    """Trim every series to the earliest "last available date" among them,
    so a multi-series comparison chart's lines all end on the same period
    instead of whichever series happens to have the most recent data point.

    Needed where two series nominally cover the same periods but one runs
    ahead of the other in practice — e.g. CBO Potential GDP is a smooth
    projection with a value for the current quarter already, while Real GDP
    (actual) lags behind by the usual ~1-month release delay, so without
    this the two lines visibly end at different quarters.
    """
    non_empty = [series.dropna() for series in series_list if not series.dropna().empty]
    if not non_empty:
        return list(series_list)
    common_end = min(series.index.max() for series in non_empty)
    return [drop_future(series, as_of=common_end) for series in series_list]
