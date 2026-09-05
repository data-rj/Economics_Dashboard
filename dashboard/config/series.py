"""FRED series IDs and non-FRED source config, grouped by dashboard section.

IDs below were verified against fred.stlouisfed.org (see research notes).
Remaining low-confidence spot: Y001RY2Q224SBEA is pattern-inferred, not
directly confirmed — double check on FRED if that chart looks off. There is
no clean native FRED bucket for LFPR 65+ or a combined 16-24 group, so the
age-participation chart uses the buckets FRED actually publishes (16-19,
25-54, 55+) rather than the originally-requested cut points.
"""

# ---- GDP / Economic Overview ----
REAL_GDP = "GDPC1"  # Real GDP, quarterly, SAAR, chained $ -> used for YoY%
GDP_QOQ_ANNUALIZED = "A191RL1Q225SBEA"  # Real GDP, % change from preceding period, annual rate
GDP_NOMINAL = "GDP"  # Nominal GDP, quarterly SAAR
GDPNOW = "GDPNOW"  # Atlanta Fed GDPNow (published on FRED)
GDP_POTENTIAL = "GDPPOT"  # CBO Real Potential GDP, quarterly

NY_FED_NOWCAST_URL = (
    "https://www.newyorkfed.org/medialibrary/Research/Interactives/Data/NowCast/"
    "Downloads/New-York-Fed-Staff-Nowcast_download_data.xlsx"
)

# Contributions to % change in real GDP (BEA NIPA table 1.1.2)
GDP_CONTRIB_PCE = "DPCERY2Q224SBEA"
GDP_CONTRIB_INVESTMENT = "A006RY2Q224SBEA"
GDP_CONTRIB_NET_EXPORTS = "A019RY2Q224SBEA"
GDP_CONTRIB_GOVERNMENT = "A822RY2Q224SBEA"

# ---- Labor Market ----
UNRATE = "UNRATE"
U6RATE = "U6RATE"
PAYEMS = "PAYEMS"  # Total nonfarm payrolls, level, thousands
AVG_HOURLY_EARNINGS = "CES0500000003"
INITIAL_CLAIMS = "ICSA"
INITIAL_CLAIMS_4WK_AVG = "IC4WSA"
JOLTS_OPENINGS = "JTSJOL"
JOLTS_QUITS = "JTSQUL"

LFPR_TOTAL = "CIVPART"
LFPR_16_19 = "LNS11300012"
LFPR_25_54 = "LNS11300060"
LFPR_55_PLUS = "LNS11324230"

# ---- The Consumer ----
REAL_PCE = "PCEC96"
REAL_DPI = "DSPIC96"
PERSONAL_SAVINGS_RATE = "PSAVERT"
RETAIL_SALES = "RSAFS"
RETAIL_SALES_EX_AUTOS = "RSFSXMV"
PCE_SERVICES_REAL = "PCESC96"

HH_DSR_TOTAL = "TDSP"
HH_DSR_MORTGAGE = "MDSP"
HH_DSR_NON_MORTGAGE = "CDSP"  # native "consumer" (non-mortgage) DSR series

DELINQ_CONSUMER_BROAD = "DRCLACBS"
DELINQ_MORTGAGE = "DRSFRMACBS"
DELINQ_CREDIT_CARD = "DRCCLACBS"

# ---- Corporate America ----
CORPORATE_PROFITS = "CPATAX"  # after-tax w/ IVA & CCAdj — the "headline" profits figure
INDUSTRIAL_PRODUCTION = "INDPRO"
CAPACITY_UTILIZATION = "TCU"

BOND_SPREAD_BBB = "BAMLC0A4CBBB"
BOND_SPREAD_BB = "BAMLH0A1HYBB"
BOND_SPREAD_B = "BAMLH0A2HYB"
BOND_SPREAD_CCC = "BAMLH0A3HYC"

BUSINESS_LOAN_DELINQ = "DRBLACBS"
BUSINESS_LOAN_CHARGEOFF = "CORBLACBS"

# ---- Investment ----
NONRESIDENTIAL_FIXED_INVESTMENT_REAL = "PNFIC1"
RESIDENTIAL_FIXED_INVESTMENT_REAL = "PRFIC1"

# Contribution of each component to the growth of Nonresidential Fixed
# Investment itself (BEA table 5.3.2, "RZ2" suffix) — not to overall GDP
# growth (that would be the "RY2" siblings A009/Y033/Y001RY2Q224SBEA).
INVESTMENT_CONTRIB_STRUCTURES = "B009RZ2Q224SBEA"
INVESTMENT_CONTRIB_EQUIPMENT = "Y033RZ2Q224SBEA"
INVESTMENT_CONTRIB_IP_PRODUCTS = "Y001RZ2Q224SBEA"

HOUSING_STARTS = "HOUST"
HOUSING_PERMITS = "PERMIT"

BUSINESS_INVENTORIES = "BUSINV"
INVENTORY_SALES_RATIO = "ISRATIO"

# ---- Government ----
GOV_CONSUMPTION_INVESTMENT_REAL = "GCEC1"
FEDERAL_RECEIPTS = "FGRECPT"
FEDERAL_OUTLAYS = "FGEXPND"
FEDERAL_DEFICIT_MONTHLY = "MTSDS133FMS"
FEDERAL_DEBT_PCT_GDP = "GFDEGDQ188S"

# ---- Prices & Monetary Policy ----
CPI = "CPIAUCSL"
CORE_CPI = "CPILFESL"
TRIMMED_MEAN_CPI = "TRMMEANCPIM159SFRBCLE"

PCE_DEFLATOR = "PCEPI"
CORE_PCE_DEFLATOR = "PCEPILFE"
TRIMMED_MEAN_PCE = "PCETRIM12M159SFRBDAL"

FED_FUNDS_RATE_DAILY = "DFF"
TREASURY_10Y = "DGS10"
TREASURY_10Y_2Y_SPREAD = "T10Y2Y"

M2_MONEY_SUPPLY = "M2SL"
M2_VELOCITY = "M2V"
FED_TOTAL_ASSETS = "WALCL"
