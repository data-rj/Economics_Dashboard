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

- The **Home** page shows every section's headline tiles; each section page
  adds its charts, two to a row on wide screens.
- Every chart defaults to **5 years** of history, with one-click range
  buttons (**1Y / 5Y / 10Y / 20Y / Max**) on each chart and a sidebar
  control that sets the range for all charts at once. Underlying transforms
  (YoY%, moving averages, etc.) are always computed over the full series
  first, so shrinking the window never distorts the math.
- Every legend entry embeds each series' **most recent value and period**
  (e.g. "Unemployment Rate (U-3) — 4.1% (Aug 2026)"). Every KPI tile shows
  the change from the previous observation; a sub-figure is tagged with its
  own period whenever that differs from the headline's.
- Quarterly data is dated at quarter-end, and gray bands mark NBER
  recessions.
- A handful of charts use a second y-axis (industrial production vs.
  capacity utilization, the manufacturing orders/inventories ratios, bank
  loan growth vs. loss allowance, the inventory-to-sales ratio, and federal
  debt as % of GDP vs. % of wealth) — a deliberate
  exception made only where the spec calls for a paired second axis; axis
  color coding keeps the two scales unambiguous and only the left axis
  draws gridlines.
- Payrolls and jobless-claims charts keep their y-axis on the typical range
  so the 2020 spike doesn't flatten everything else; a "Full y-range"
  toggle shows the extremes.
- CBO Potential GDP (`GDPPOT`) is published with a forecast horizon running
  years past today — the app truncates it to the latest quarter that actual
  GDP is available for before computing YoY%.
- Data is cached for an hour; the sidebar shows when FRED was last queried
  and has a **Refresh data** button.
- If a data source fails (network issue, an upstream layout change), that
  one tile shows "Data unavailable" (hover for the detail) and that one
  chart shows "No data available" with the error tucked into a collapsed
  expander — one bad series never breaks the rest of the page. With no API
  key at all, the app shows a single notice instead of loading pages. FRED
  API keys are redacted from any error text before it reaches the UI.

## Known caveats

- The **NY Fed Staff Nowcast** is a weekly Excel file with no stable public
  API or documented schema; the parser reads the latest release row from
  the release-dated sheet and falls back to an older layout defensively.
  If the NY Fed changes their file layout, that one KPI tile will show
  "Data unavailable" rather than a stale/wrong number.
- A few FRED series IDs were the best available match for a requested
  concept and are called out in `dashboard/config/series.py`:
  - Labor force participation by age uses the buckets FRED actually
    publishes (16-19, 25-54, 55+) — there's no clean native 16-24 or 65+
    breakout.
  - The nonresidential investment contribution chart uses BEA's
    contributions to the % change in real *private fixed investment*
    (`B009RZ2…`, `Y033RZ2…`, `Y001RZ2…`), not contributions to GDP growth.
  - The ICE BofA high-yield OAS series (bond spreads by rating) may have
    truncated history per ICE's data licensing terms — check the "Max"
    range if a spread chart looks shorter than expected.
