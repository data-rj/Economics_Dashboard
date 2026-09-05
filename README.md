# U.S. Economic Dashboard

A Streamlit dashboard covering the U.S. economy across seven sections:
Economic Overview, Labor Market, The Consumer, Corporate America, Public &
Private Investment, Government, and Prices & Monetary Policy.

Data comes from the [FRED API](https://fred.stlouisfed.org/docs/api/fred/)
(St. Louis Fed), the Atlanta Fed's GDPNow (also published on FRED), and the
New York Fed's weekly Staff Nowcast (downloaded directly as Excel — it has
no API).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Get a free FRED API key at https://fred.stlouisfed.org/docs/api/api_key.html,
then provide it one of three ways:

1. **Environment variable**: `export FRED_API_KEY=your_key_here`
2. **Streamlit secrets**: create `.streamlit/secrets.toml` with
   `FRED_API_KEY = "your_key_here"` (gitignored)
3. **In-app**: paste it into the sidebar text box at runtime — it's kept
   only in that browser session's memory, never written to disk

## Run

```bash
streamlit run app.py
```

## Design notes

- Every chart defaults to **5 years** of history, with a per-chart control
  to expand to the full available history (**Max**) or narrow to **1 year**.
  Underlying transforms (YoY%, moving averages, etc.) are always computed
  over the full series first, so shrinking the window never distorts the
  math.
- Every legend entry embeds each series' **most recent value and period**
  (e.g. "Unemployment Rate (U-3) — 4.1% (Aug 2026)").
- A handful of charts use a second y-axis (industrial production vs.
  capacity utilization, the inventory-to-sales ratio, M2 vs. velocity, and
  the federal deficit vs. debt/GDP) — that's a deliberate exception made
  only where the spec explicitly calls for a paired second axis; axis
  color coding keeps the two scales unambiguous.
- CBO Potential GDP (`GDPPOT`) is published with a forecast horizon running
  years past today — the app truncates it to actual history before
  computing YoY% or the output gap.
- If a data source fails (missing key, network issue, an upstream layout
  change), that one chart shows "No data available" with the error
  detail tucked into a collapsed expander — one bad series never breaks
  the rest of the page. FRED API keys are redacted from any error text
  before it reaches the UI.

## Known caveats

- The **NY Fed Staff Nowcast** is a weekly Excel file with no stable public
  API or documented schema; the parser scans every sheet for a row labeled
  "Nowcast" defensively. If the NY Fed changes their file layout, that one
  KPI tile will show an error rather than a stale/wrong number.
- A few FRED series IDs were the best available match for a requested
  concept and are called out in `dashboard/config/series.py`:
  - Labor force participation by age uses the buckets FRED actually
    publishes (16-19, 25-54, 55+) — there's no clean native 16-24 or 65+
    breakout.
  - `Y001RY2Q224SBEA` (IP products' contribution to GDP, used only as a
    cross-check note, not wired into a chart) is pattern-inferred rather
    than directly confirmed.
  - The ICE BofA high-yield OAS series (bond spreads by rating) may have
    truncated history per ICE's data licensing terms — check the "Max"
    range if a spread chart looks shorter than expected.
