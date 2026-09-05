"""App-wide constants: branding, palette, and chart defaults."""

APP_TITLE = "U.S. Economic Dashboard"

# Fixed categorical hue order (never cycled/reassigned) — validated for
# CVD-safe adjacent contrast. See dataviz skill references/palette.md.
CATEGORICAL = {
    "blue": "#2a78d6",
    "orange": "#eb6834",
    "aqua": "#1baf7a",
    "yellow": "#eda100",
    "magenta": "#e87ba4",
    "green": "#008300",
    "violet": "#4a3aa7",
    "red": "#e34948",
}
CATEGORICAL_ORDER = list(CATEGORICAL.values())

DIVERGING_POS = "#2a78d6"  # blue
DIVERGING_NEG = "#e34948"  # red
DIVERGING_MID = "#9c9c96"  # neutral gray

STATUS = {
    "good": "#0ca30c",
    "warning": "#fab219",
    "serious": "#ec835a",
    "critical": "#d03b3b",
}

GRID_COLOR = "rgba(128,128,128,0.20)"
ZERO_LINE_COLOR = "rgba(128,128,128,0.45)"
AXIS_LINE_COLOR = "rgba(128,128,128,0.35)"

# FRED API
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
CACHE_TTL_SECONDS = 60 * 60  # 1 hour

# NY Fed Staff Nowcast (weekly Excel release) — verified download URL lives
# in dashboard/config/series.py alongside the rest of the source config.
