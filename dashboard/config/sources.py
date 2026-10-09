"""Maps each FRED series ID used by the dashboard to its originating
agency, for the "Source:" caption shown under every chart. Keyed by the
literal FRED series ID (not the python constant name) so callers can just
pass the same ID strings they already use to fetch data.
"""

BEA = "U.S. Bureau of Economic Analysis"
BLS = "U.S. Bureau of Labor Statistics"
CENSUS = "U.S. Census Bureau"
TREASURY = "U.S. Department of the Treasury"
CBO = "Congressional Budget Office"
FED_BOARD = "Board of Governors of the Federal Reserve System"
FRBSL = "Federal Reserve Bank of St. Louis"
FRB_ATLANTA = "Federal Reserve Bank of Atlanta"
FRB_CLEVELAND = "Federal Reserve Bank of Cleveland"
FRB_DALLAS = "Federal Reserve Bank of Dallas"
ETA = "U.S. Employment and Training Administration"
ICE = "ICE Data Indices, LLC"

SOURCE_AGENCY: dict[str, str] = {
    # GDP / Economic Overview
    "GDPC1": BEA,
    "A191RL1Q225SBEA": BEA,
    "GDP": BEA,
    "GDPNOW": FRB_ATLANTA,
    "GDPPOT": CBO,
    "DPCERY2Q224SBEA": BEA,
    "A006RY2Q224SBEA": BEA,
    "A019RY2Q224SBEA": BEA,
    "A822RY2Q224SBEA": BEA,
    # Labor Market
    "UNRATE": BLS,
    "U6RATE": BLS,
    "PAYEMS": BLS,
    "CES0500000003": BLS,
    "ICSA": ETA,
    "IC4WSA": ETA,
    "JTSJOL": BLS,
    "JTSQUL": BLS,
    "CIVPART": BLS,
    "LNS11300012": BLS,
    "LNS11300060": BLS,
    "LNS11324230": BLS,
    # The Consumer
    "PCEC96": BEA,
    "DSPIC96": BEA,
    "PSAVERT": BEA,
    "RSAFS": CENSUS,
    "RSFSXMV": CENSUS,
    "PCESC96": BEA,
    "TDSP": FED_BOARD,
    "MDSP": FED_BOARD,
    "CDSP": FED_BOARD,
    "DRCLACBS": FED_BOARD,
    "DRSFRMACBS": FED_BOARD,
    "DRCCLACBS": FED_BOARD,
    # Corporate America
    "CPATAX": BEA,
    "INDPRO": FED_BOARD,
    "TCU": FED_BOARD,
    "BAMLC0A4CBBB": ICE,
    "BAMLH0A1HYBB": ICE,
    "BAMLH0A2HYB": ICE,
    "BAMLH0A3HYC": ICE,
    "DRBLACBS": FED_BOARD,
    "CORBLACBS": FED_BOARD,
    # Investment
    "PNFIC1": BEA,
    "PRFIC1": BEA,
    "B009RZ2Q224SBEA": BEA,
    "Y033RZ2Q224SBEA": BEA,
    "Y001RZ2Q224SBEA": BEA,
    "HOUST": CENSUS,
    "PERMIT": CENSUS,
    "BUSINV": CENSUS,
    "ISRATIO": CENSUS,
    # Government
    "GCEC1": BEA,
    "FGRECPT": BEA,
    "FGEXPND": BEA,
    "MTSDS133FMS": TREASURY,
    "GFDEGDQ188S": TREASURY,
    # Prices & Monetary Policy
    "CPIAUCSL": BLS,
    "CPILFESL": BLS,
    "TRMMEANCPIM159SFRBCLE": FRB_CLEVELAND,
    "PCEPI": BEA,
    "PCEPILFE": BEA,
    "PCETRIM12M159SFRBDAL": FRB_DALLAS,
    "T5YIE": FRBSL,
    "T10YIE": FRBSL,
    "DFF": FED_BOARD,
    "DGS10": FED_BOARD,
    "T10Y2Y": FRBSL,
    "M2SL": FED_BOARD,
    "M2V": FRBSL,
    "WALCL": FED_BOARD,
}

NY_FED_NOWCAST_AGENCY = "Federal Reserve Bank of New York"


def fred_source_caption(series_ids: list[str]) -> str:
    """'Source: <agency(ies)> via FRED (<series IDs>).'"""
    agencies: list[str] = []
    for sid in series_ids:
        agency = SOURCE_AGENCY.get(sid, "FRED")
        if agency not in agencies:
            agencies.append(agency)
    return f"Source: {', '.join(agencies)} via FRED ({', '.join(series_ids)})."
