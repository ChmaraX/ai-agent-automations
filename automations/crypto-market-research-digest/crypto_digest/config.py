from __future__ import annotations

from pathlib import Path

AUTOMATION_ID = "crypto-market-research-digest"
DEFAULT_PAIRS = [
    "BTCUSDT",
    "ETHUSDT",
    "SOLUSDT",
    "BNBUSDT",
    "XRPUSDT",
    "DOGEUSDT",
    "ADAUSDT",
    "AVAXUSDT",
    "LINKUSDT",
]
DEFAULT_WATCHLIST = [
    "COIN",
    "MSTR",
    "MARA",
    "RIOT",
    "XYZ",
    "PYPL",
    "HOOD",
    "CLSK",
    "HUT",
    "BTBT",
    "CAN",
    "IREN",
    "WULF",
    "BITF",
]
SEC_CIK_OVERRIDES = {"BITF": "0001812477", "SQ": "XYZ"}
SEC_PRIORITY_FORMS = {
    "10-K",
    "10-Q",
    "8-K",
    "S-1",
    "S-3",
    "F-1",
    "20-F",
    "40-F",
    "6-K",
    "N-1A",
    "N-2",
    "NPORT-P",
}
SEC_PRIORITY_FORM_PREFIXES = ("424B",)
SEC_USER_AGENT = "crypto-market-research-digest/1.0 research@example.com"
BINANCE_ENDPOINT = "https://data-api.binance.vision/api/v3/ticker/24hr"
BINANCE_KLINES_ENDPOINT = "https://data-api.binance.vision/api/v3/klines"
BINANCE_CANDLE_FEATURED_PAIRS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]
BINANCE_CANDLE_INTERVAL = "1h"
BINANCE_CANDLE_LIMIT = 24
DEFILLAMA_PROTOCOLS = "https://api.llama.fi/protocols"
DEFILLAMA_CHAINS = "https://api.llama.fi/v2/chains"
DEFILLAMA_STABLECOINS = "https://stablecoins.llama.fi/stablecoins?includePrices=true"
DEFILLAMA_FEES = "https://api.llama.fi/overview/fees"
DEFILLAMA_DEXS = "https://api.llama.fi/overview/dexs"
DEFILLAMA_YIELDS = "https://yields.llama.fi/pools"
SEC_TICKERS = "https://www.sec.gov/files/company_tickers.json"
SEC_SUBMISSIONS = "https://data.sec.gov/submissions/CIK{cik}.json"
OFAC_SDN_XML = "https://www.treasury.gov/ofac/downloads/sdn.xml"
OFAC_CONSOLIDATED_XML = "https://www.treasury.gov/ofac/downloads/consolidated/consolidated.xml"
STATE_DIRNAME = ".automation-state/crypto-market-research-digest"
STATE_FILENAME = "previous_run_state.json"
SNAPSHOT_FILENAME = "current_snapshot.json"
REPORTS_DIRNAME = "reports"
CACHE_DIRNAME = "cache"
SEC_TICKER_CACHE_FILENAME = "sec_company_tickers.json"
SEC_TICKER_CACHE_TTL_SECONDS = 24 * 60 * 60
TOP_CHAIN_COUNT = 5
TOP_PROTOCOL_COUNT = 5
TOP_FEES_COUNT = 5
TOP_DEX_COUNT = 5
TOP_STABLECOIN_ASSET_COUNT = 3
TOP_STABLECOIN_CHAIN_COUNT = 5
TOP_YIELD_COUNT = 6
YIELD_PRIMARY_TVL_THRESHOLD = 5_000_000
YIELD_SECONDARY_TVL_THRESHOLD = 1_000_000
YIELD_APY_THRESHOLD = 25.0
YIELD_EXTREME_APY_THRESHOLD = 1_000.0
STABLECOIN_CHAIN_MOVE_THRESHOLD = 5.0
PROTOCOL_MOVE_THRESHOLD = 10.0
FEE_DEX_MOVE_THRESHOLD = 20.0
KNOWN_PROTOCOLS = {
    "aave",
    "aerodrome",
    "curve",
    "euler",
    "ethena",
    "jupiter",
    "kamino",
    "lido",
    "morpho",
    "morpho-blue",
    "pendle",
    "spark",
}
MINER_TICKERS = {"MARA", "RIOT", "CLSK", "HUT", "BTBT", "CAN", "IREN", "WULF", "BITF"}
PREFERRED_OFAC_NAMES = {
    "HYDRA MARKET",
    "BLENDER.IO",
    "SUEX OTC, S.R.O.",
    "LAZARUS GROUP",
    "SINBAD",
    "GARANTEX EUROPE OU",
    "CHATEX",
    "CHEIL CREDIT BANK",
}


def state_dir(workspace: Path) -> Path:
    return workspace / STATE_DIRNAME


def state_path(workspace: Path) -> Path:
    return state_dir(workspace) / STATE_FILENAME


def snapshot_path(workspace: Path) -> Path:
    return state_dir(workspace) / SNAPSHOT_FILENAME


def reports_dir(workspace: Path) -> Path:
    return state_dir(workspace) / REPORTS_DIRNAME


def cache_dir(workspace: Path) -> Path:
    return state_dir(workspace) / CACHE_DIRNAME
