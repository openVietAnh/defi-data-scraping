"""Shared configuration for the AAVE V2 DeFi scraping pipeline.

Defines tokens, API endpoints, data paths, and collection constants.
All scripts import from here — never hardcode these values elsewhere.
"""

import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUT_DIR = DATA_DIR / "output"

# ── Token configuration ────────────────────────────────────────────────────

# ERC-20 decimal places per token
TOKEN_DECIMALS: dict = {
    "DAI":  18,
    "WBTC": 8,
    "WETH": 18,
    "USDC": 6,
    "USDT": 6,
}

TOKENS = list(TOKEN_DECIMALS.keys())

# AAVE V2 reserve IDs (token symbol → composite subgraph reserve id)
RESERVE_IDS: dict = {
    "DAI":  "0x6b175474e89094c44da98b954eedeac495271d0f0xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
    "WBTC": "0x2260fac5e5542a773aa44fbcfedf7c193bc2c5990xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
    "WETH": "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc20xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
    "USDC": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb480xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
    "USDT": "0xdac17f958d2ee523a2206206994597c13d831ec70xb53c1a33016b2dc2ff3653530bff1848a515c8c5",
}

# ── API endpoints ──────────────────────────────────────────────────────────

def get_aave_subgraph_url() -> str:
    """Return the authenticated AAVE V2 subgraph URL. Raises if API_KEY is unset."""
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise EnvironmentError("API_KEY environment variable is not set.")
    return (
        f"https://gateway-arbitrum.network.thegraph.com/api/{api_key}"
        "/subgraphs/id/8wR23o1zkS4gpLqLNU4kG3JHYVucqGyopL5utGxP2q1N"
    )


# Legacy AAVE V2 subgraph (no key required; used for price history endpoints)
AAVE_LEGACY_URL = "https://api.thegraph.com/subgraphs/name/aave/protocol-v2"


def get_alchemy_url() -> str:
    """Return the Alchemy ETH node URL. Reads from ALCHEMY_URL env var."""
    url = os.environ.get("ALCHEMY_URL")
    if not url:
        raise EnvironmentError("ALCHEMY_URL environment variable is not set.")
    return url


# ── Collection window ──────────────────────────────────────────────────────

# Default data collection range (Unix timestamps)
COLLECTION_START_TIMESTAMP = 1606777900  # 2020-11-30 — earliest WETH data
COLLECTION_END_TIMESTAMP   = 1659286703  # 2022-07-31

# ── Financial constants ────────────────────────────────────────────────────

SECONDS_PER_YEAR = 31_556_926  # seconds in a solar year (used for APY)
RAY = 10 ** 27                 # AAVE V2 ray unit (rates stored as ray values)

# ── Transaction types ──────────────────────────────────────────────────────

TRANSACTION_TYPES = (
    "borrow",
    "deposit",
    "flashLoan",
    "liquidationCall",
    "redeemUnderlying",
    "repay",
    "swap",
    "usageAsCollateral",
    "rebalanceStableBorrowRate",
)
