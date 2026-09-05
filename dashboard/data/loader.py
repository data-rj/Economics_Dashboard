"""Section-level data loaders: each function fetches raw FRED series, applies
the needed transform (YoY%, annualized rate, moving average, ratio, ...) over
the FULL available history, and returns a dict of {label: pd.Series} plus a
dict of {label: error_message}. Date-range clipping for display happens later
in the chart layer (components/controls.py) so moving averages / YoY math is
never computed on a pre-truncated window.
"""
from __future__ import annotations

import pandas as pd

from dashboard.config import series as s
from dashboard.data.fred_client import safe_fetch_series
from dashboard.data.nowcasts import get_nyfed_nowcast
from dashboard.utils.transforms import (
    diff,
    drop_future,
    moving_average,
    pct_of,
    period_annualized_pct,
    resample_mean,
    trailing_sum,
    yoy_pct,
)

START = "1990-01-01"


def _fetch(series_id: str) -> tuple[pd.Series, str | None]:
    return safe_fetch_series(series_id, START)


# ---------------- Economic Overview ----------------

def load_gdp_kpis() -> list[dict]:
    real_gdp, e1 = _fetch(s.REAL_GDP)
    gdp_qoq, e2 = _fetch(s.GDP_QOQ_ANNUALIZED)
    gdpnow, e3 = _fetch(s.GDPNOW)
    nyfed_value, nyfed_period, e4 = get_nyfed_nowcast()

    gdp_yoy = yoy_pct(real_gdp, "Q").dropna()
    gdp_qoq_clean = gdp_qoq.dropna()
    gdpnow_clean = gdpnow.dropna()

    items = [
        {
            "label": "Real GDP YoY%",
            "value": gdp_yoy.iloc[-1] if not gdp_yoy.empty else None,
            "unit": "pct",
            "period": gdp_yoy.index[-1].strftime("%b %Y") if not gdp_yoy.empty else None,
            "error": e1 if gdp_yoy.empty else None,
        },
        {
            "label": "GDP QoQ Annualized",
            "value": gdp_qoq_clean.iloc[-1] if not gdp_qoq_clean.empty else None,
            "unit": "pct",
            "period": gdp_qoq_clean.index[-1].strftime("%b %Y") if not gdp_qoq_clean.empty else None,
            "error": e2 if gdp_qoq_clean.empty else None,
        },
        {
            "label": "Atlanta Fed GDPNow",
            "value": gdpnow_clean.iloc[-1] if not gdpnow_clean.empty else None,
            "unit": "pct",
            "period": gdpnow_clean.index[-1].strftime("%b %Y") if not gdpnow_clean.empty else None,
            "error": e3 if gdpnow_clean.empty else None,
        },
        {
            "label": "NY Fed Staff Nowcast",
            "value": nyfed_value,
            "unit": "pct",
            "period": nyfed_period,
            "error": e4 if nyfed_value is None else None,
        },
    ]
    return items


def load_gdp_growth_lines() -> tuple[dict[str, pd.Series], dict[str, str]]:
    real_gdp, e1 = _fetch(s.REAL_GDP)
    gdp_qoq, e2 = _fetch(s.GDP_QOQ_ANNUALIZED)
    data = {
        "Real GDP YoY%": yoy_pct(real_gdp, "Q"),
        "Real GDP QoQ Annualized": gdp_qoq,
    }
    errors = {"Real GDP YoY%": e1, "Real GDP QoQ Annualized": e2}
    return data, errors


def load_gdp_contributions() -> tuple[dict[str, pd.Series], dict[str, str]]:
    pce, e1 = _fetch(s.GDP_CONTRIB_PCE)
    inv, e2 = _fetch(s.GDP_CONTRIB_INVESTMENT)
    nx, e3 = _fetch(s.GDP_CONTRIB_NET_EXPORTS)
    gov, e4 = _fetch(s.GDP_CONTRIB_GOVERNMENT)
    data = {
        "Personal Consumption": pce,
        "Private Investment": inv,
        "Net Exports": nx,
        "Government": gov,
    }
    errors = {
        "Personal Consumption": e1,
        "Private Investment": e2,
        "Net Exports": e3,
        "Government": e4,
    }
    return data, errors


def load_gdp_actual_vs_potential() -> tuple[dict[str, pd.Series], dict[str, str]]:
    real_gdp, e1 = _fetch(s.REAL_GDP)
    potential, e2 = _fetch(s.GDP_POTENTIAL)
    data = {
        "Real GDP (Actual) YoY%": yoy_pct(real_gdp, "Q"),
        "Potential GDP (CBO) YoY%": drop_future(yoy_pct(potential, "Q")),
    }
    errors = {"Real GDP (Actual) YoY%": e1, "Potential GDP (CBO) YoY%": e2}
    return data, errors


def load_output_gap() -> tuple[dict[str, pd.Series], dict[str, str]]:
    real_gdp, e1 = _fetch(s.REAL_GDP)
    potential, e2 = _fetch(s.GDP_POTENTIAL)
    potential = drop_future(potential)
    gap = pct_of(real_gdp - potential, potential)
    return {"Output Gap (% of Potential GDP)": gap}, {"Output Gap (% of Potential GDP)": e1 or e2}


# ---------------- Labor Market ----------------

def load_unemployment_rates() -> tuple[dict[str, pd.Series], dict[str, str]]:
    unrate, e1 = _fetch(s.UNRATE)
    u6, e2 = _fetch(s.U6RATE)
    return {"Unemployment Rate (U-3)": unrate, "Broader Unemployment (U-6)": u6}, {
        "Unemployment Rate (U-3)": e1,
        "Broader Unemployment (U-6)": e2,
    }


def load_payrolls_change() -> tuple[pd.Series, pd.Series, str | None]:
    payems, e1 = _fetch(s.PAYEMS)
    change = diff(payems)
    avg3 = moving_average(change, 3)
    return change, avg3, e1


def load_avg_hourly_earnings() -> tuple[dict[str, pd.Series], dict[str, str]]:
    ahe, e1 = _fetch(s.AVG_HOURLY_EARNINGS)
    data = {
        "Avg Hourly Earnings YoY%": yoy_pct(ahe, "M"),
        "Avg Hourly Earnings, Monthly Annualized": period_annualized_pct(ahe, "M"),
    }
    return data, {k: e1 for k in data}


def load_jobless_claims() -> tuple[dict[str, pd.Series], dict[str, str]]:
    claims, e1 = _fetch(s.INITIAL_CLAIMS)
    avg4wk, e2 = _fetch(s.INITIAL_CLAIMS_4WK_AVG)
    return {"Initial Jobless Claims": claims, "4-Week Moving Average": avg4wk}, {
        "Initial Jobless Claims": e1,
        "4-Week Moving Average": e2,
    }


def load_jolts() -> tuple[dict[str, pd.Series], dict[str, str]]:
    openings, e1 = _fetch(s.JOLTS_OPENINGS)
    quits, e2 = _fetch(s.JOLTS_QUITS)
    return {"Job Openings": openings, "Quits": quits}, {"Job Openings": e1, "Quits": e2}


def load_lfpr_by_age() -> tuple[dict[str, pd.Series], dict[str, str]]:
    total, e0 = _fetch(s.LFPR_TOTAL)
    y, e1 = _fetch(s.LFPR_16_19)
    prime, e2 = _fetch(s.LFPR_25_54)
    older, e3 = _fetch(s.LFPR_55_PLUS)
    data = {
        "Total": total,
        "Ages 16-19": y,
        "Ages 25-54 (Prime)": prime,
        "Ages 55+": older,
    }
    errors = {"Total": e0, "Ages 16-19": e1, "Ages 25-54 (Prime)": e2, "Ages 55+": e3}
    return data, errors


# ---------------- The Consumer ----------------

def load_pce_income_savings() -> tuple[dict[str, pd.Series], dict[str, str]]:
    pce, e1 = _fetch(s.REAL_PCE)
    dpi, e2 = _fetch(s.REAL_DPI)
    savings, e3 = _fetch(s.PERSONAL_SAVINGS_RATE)
    data = {
        "Real PCE YoY%": yoy_pct(pce, "M"),
        "Real Disposable Income YoY%": yoy_pct(dpi, "M"),
        "Personal Savings Rate": savings,
    }
    return data, {"Real PCE YoY%": e1, "Real Disposable Income YoY%": e2, "Personal Savings Rate": e3}


def load_retail_sales() -> tuple[dict[str, pd.Series], dict[str, str]]:
    retail, e1 = _fetch(s.RETAIL_SALES)
    retail_ex_auto, e2 = _fetch(s.RETAIL_SALES_EX_AUTOS)
    pce_services, e3 = _fetch(s.PCE_SERVICES_REAL)
    data = {
        "Retail Sales YoY%": yoy_pct(retail, "M"),
        "Retail Sales ex-Autos YoY%": yoy_pct(retail_ex_auto, "M"),
        "PCE Services YoY%": yoy_pct(pce_services, "M"),
    }
    return data, {"Retail Sales YoY%": e1, "Retail Sales ex-Autos YoY%": e2, "PCE Services YoY%": e3}


def load_household_dsr() -> tuple[dict[str, pd.Series], dict[str, str]]:
    total, e1 = _fetch(s.HH_DSR_TOTAL)
    mortgage, e2 = _fetch(s.HH_DSR_MORTGAGE)
    non_mortgage, e3 = _fetch(s.HH_DSR_NON_MORTGAGE)
    data = {
        "Total Debt Service Ratio": total,
        "Mortgage Debt Service Ratio": mortgage,
        "Non-Mortgage Debt Service Ratio": non_mortgage,
    }
    return data, {
        "Total Debt Service Ratio": e1,
        "Mortgage Debt Service Ratio": e2,
        "Non-Mortgage Debt Service Ratio": e3,
    }


def load_delinquencies() -> tuple[dict[str, pd.Series], dict[str, str]]:
    broad, e1 = _fetch(s.DELINQ_CONSUMER_BROAD)
    mortgage, e2 = _fetch(s.DELINQ_MORTGAGE)
    cc, e3 = _fetch(s.DELINQ_CREDIT_CARD)
    data = {"Consumer Loans (Broad)": broad, "Mortgages": mortgage, "Credit Cards": cc}
    return data, {"Consumer Loans (Broad)": e1, "Mortgages": e2, "Credit Cards": e3}


# ---------------- Corporate America ----------------

def load_corporate_profits_yoy() -> tuple[dict[str, pd.Series], dict[str, str]]:
    cp, e1 = _fetch(s.CORPORATE_PROFITS)
    return {"Corporate Profits YoY%": yoy_pct(cp, "Q")}, {"Corporate Profits YoY%": e1}


def load_corporate_profits_share_gdp() -> tuple[dict[str, pd.Series], dict[str, str]]:
    cp, e1 = _fetch(s.CORPORATE_PROFITS)
    gdp, e2 = _fetch(s.GDP_NOMINAL)
    share = pct_of(cp, gdp)
    return {"Corporate Profits (% of GDP)": share}, {"Corporate Profits (% of GDP)": e1 or e2}


def load_industrial_production() -> tuple[dict[str, pd.Series], dict[str, str]]:
    indpro, e1 = _fetch(s.INDUSTRIAL_PRODUCTION)
    tcu, e2 = _fetch(s.CAPACITY_UTILIZATION)
    return {
        "left": ("Industrial Production YoY%", yoy_pct(indpro, "M"), "pct"),
        "right": ("Capacity Utilization", tcu, "pct"),
    }, {"Industrial Production YoY%": e1, "Capacity Utilization": e2}


def load_bond_spreads() -> tuple[dict[str, pd.Series], dict[str, str]]:
    bbb, e1 = _fetch(s.BOND_SPREAD_BBB)
    bb, e2 = _fetch(s.BOND_SPREAD_BB)
    b, e3 = _fetch(s.BOND_SPREAD_B)
    ccc, e4 = _fetch(s.BOND_SPREAD_CCC)
    data = {"Baa/BBB": bbb, "Ba/BB": bb, "B": b, "CCC": ccc}
    return data, {"Baa/BBB": e1, "Ba/BB": e2, "B": e3, "CCC": e4}


def load_corporate_delinquency_chargeoff() -> tuple[dict[str, pd.Series], dict[str, str]]:
    delinq, e1 = _fetch(s.BUSINESS_LOAN_DELINQ)
    chargeoff, e2 = _fetch(s.BUSINESS_LOAN_CHARGEOFF)
    return {"Delinquency Rate": delinq, "Charge-Off Rate": chargeoff}, {
        "Delinquency Rate": e1,
        "Charge-Off Rate": e2,
    }


# ---------------- Investment ----------------

def load_fixed_investment_yoy() -> tuple[dict[str, pd.Series], dict[str, str]]:
    nonres, e1 = _fetch(s.NONRESIDENTIAL_FIXED_INVESTMENT_REAL)
    res, e2 = _fetch(s.RESIDENTIAL_FIXED_INVESTMENT_REAL)
    data = {
        "Nonresidential Fixed Investment YoY%": yoy_pct(nonres, "Q"),
        "Residential Fixed Investment YoY%": yoy_pct(res, "Q"),
    }
    return data, {
        "Nonresidential Fixed Investment YoY%": e1,
        "Residential Fixed Investment YoY%": e2,
    }


def load_investment_contributions() -> tuple[dict[str, pd.Series], dict[str, str]]:
    structures, e1 = _fetch(s.INVESTMENT_CONTRIB_STRUCTURES)
    equipment, e2 = _fetch(s.INVESTMENT_CONTRIB_EQUIPMENT)
    ip, e3 = _fetch(s.INVESTMENT_CONTRIB_IP_PRODUCTS)
    data = {"Structures": structures, "Equipment": equipment, "Intellectual Property Products": ip}
    return data, {"Structures": e1, "Equipment": e2, "Intellectual Property Products": e3}


def load_housing() -> tuple[dict[str, pd.Series], dict[str, str]]:
    starts, e1 = _fetch(s.HOUSING_STARTS)
    permits, e2 = _fetch(s.HOUSING_PERMITS)
    return {"Housing Starts": starts, "Building Permits": permits}, {
        "Housing Starts": e1,
        "Building Permits": e2,
    }


def load_inventory_ratio() -> tuple[dict[str, pd.Series], dict[str, str]]:
    inv, e1 = _fetch(s.BUSINESS_INVENTORIES)
    ratio_series, e2 = _fetch(s.INVENTORY_SALES_RATIO)
    return {
        "left": ("Business Inventories YoY%", yoy_pct(inv, "M"), "pct"),
        "right": ("Inventory-to-Sales Ratio", ratio_series, "ratio"),
    }, {"Business Inventories YoY%": e1, "Inventory-to-Sales Ratio": e2}


# ---------------- Government ----------------

def load_gov_consumption_yoy() -> tuple[dict[str, pd.Series], dict[str, str]]:
    gov, e1 = _fetch(s.GOV_CONSUMPTION_INVESTMENT_REAL)
    return {"Gov't Consumption & Investment YoY%": yoy_pct(gov, "Q")}, {
        "Gov't Consumption & Investment YoY%": e1
    }


def load_federal_outlays_receipts() -> tuple[dict[str, pd.Series], dict[str, str]]:
    receipts, e1 = _fetch(s.FEDERAL_RECEIPTS)
    outlays, e2 = _fetch(s.FEDERAL_OUTLAYS)
    return {"Federal Receipts": receipts, "Federal Outlays": outlays}, {
        "Federal Receipts": e1,
        "Federal Outlays": e2,
    }


def load_federal_deficit_debt() -> tuple[dict, dict[str, str]]:
    deficit, e1 = _fetch(s.FEDERAL_DEFICIT_MONTHLY)
    debt_pct_gdp, e2 = _fetch(s.FEDERAL_DEBT_PCT_GDP)
    ttm_deficit = trailing_sum(deficit, 12) / 1000  # millions -> billions
    data = {
        "area": ("Federal Deficit (TTM)", ttm_deficit, "usd_b"),
        "line": ("Federal Debt (% of GDP)", debt_pct_gdp, "pct"),
    }
    return data, {"Federal Deficit (TTM)": e1, "Federal Debt (% of GDP)": e2}


# ---------------- Prices & Monetary Policy ----------------

def load_cpi() -> tuple[dict[str, pd.Series], dict[str, str]]:
    cpi, e1 = _fetch(s.CPI)
    core, e2 = _fetch(s.CORE_CPI)
    trimmed, e3 = _fetch(s.TRIMMED_MEAN_CPI)
    data = {
        "CPI YoY%": yoy_pct(cpi, "M"),
        "Core CPI YoY%": yoy_pct(core, "M"),
        "Trimmed Mean CPI YoY%": trimmed,
    }
    return data, {"CPI YoY%": e1, "Core CPI YoY%": e2, "Trimmed Mean CPI YoY%": e3}


def load_pce_deflator() -> tuple[dict[str, pd.Series], dict[str, str]]:
    pce, e1 = _fetch(s.PCE_DEFLATOR)
    core, e2 = _fetch(s.CORE_PCE_DEFLATOR)
    trimmed, e3 = _fetch(s.TRIMMED_MEAN_PCE)
    data = {
        "PCE Deflator YoY%": yoy_pct(pce, "M"),
        "Core PCE Deflator YoY%": yoy_pct(core, "M"),
        "Trimmed Mean PCE YoY%": trimmed,
    }
    return data, {"PCE Deflator YoY%": e1, "Core PCE Deflator YoY%": e2, "Trimmed Mean PCE YoY%": e3}


def load_interest_rates() -> tuple[dict[str, pd.Series], dict[str, str]]:
    ffr, e1 = _fetch(s.FED_FUNDS_RATE_DAILY)
    t10y, e2 = _fetch(s.TREASURY_10Y)
    spread, e3 = _fetch(s.TREASURY_10Y_2Y_SPREAD)
    data = {
        "Fed Funds Rate (Weekly Avg)": resample_mean(ffr, "W"),
        "10-Year Treasury (Weekly Avg)": resample_mean(t10y, "W"),
        "10Y-2Y Spread (Weekly Avg)": resample_mean(spread, "W"),
    }
    return data, {
        "Fed Funds Rate (Weekly Avg)": e1,
        "10-Year Treasury (Weekly Avg)": e2,
        "10Y-2Y Spread (Weekly Avg)": e3,
    }


def load_m2() -> tuple[dict, dict[str, str]]:
    m2, e1 = _fetch(s.M2_MONEY_SUPPLY)
    velocity, e2 = _fetch(s.M2_VELOCITY)
    data = {
        "left": ("M2 Money Supply YoY%", yoy_pct(m2, "M"), "pct"),
        "right": ("M2 Velocity", velocity, "ratio"),
    }
    return data, {"M2 Money Supply YoY%": e1, "M2 Velocity": e2}


def load_fed_balance_sheet() -> tuple[dict[str, pd.Series], dict[str, str]]:
    assets, e1 = _fetch(s.FED_TOTAL_ASSETS)
    return {"Fed Total Assets": assets / 1000}, {"Fed Total Assets": e1}  # millions -> billions
