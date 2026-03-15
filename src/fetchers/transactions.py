"""Fetch AAVE V2 transaction data from The Graph subgraph.

Each public function handles backward-time pagination and returns a flat
list of dicts ready to be written to CSV.

Usage:
    python -m src.fetchers.transactions --type borrow
    python -m src.fetchers.transactions --type all   # fetches all types
"""

import argparse
import csv
import sys
from pathlib import Path

# Allow running as a script from the project root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import (
    get_aave_subgraph_url,
    AAVE_LEGACY_URL,
    COLLECTION_START_TIMESTAMP,
    COLLECTION_END_TIMESTAMP,
    RAW_DIR,
)
from src.fetchers.base import subgraph_post
from src.utils.csv_io import write_csv


# ---------------------------------------------------------------------------
# Generic paginator
# ---------------------------------------------------------------------------

def _paginate(url, entity, query_fields, flatten_fn, start_ts, end_ts):
    """Paginate backwards in time over an AAVE V2 subgraph entity.

    Fetches pages of up to 1000 records in descending timestamp order,
    de-duplicates records at page boundaries, and applies flatten_fn to
    each raw item before collecting it.

    Returns a list of flat dicts.
    """
    current_time = end_ts
    last_ids = set()
    records = []

    while True:
        query = f"""
        {{
            {entity}(
                where: {{timestamp_lte: {current_time}, timestamp_gt: {start_ts}}},
                first: 1000,
                orderBy: timestamp,
                orderDirection: desc
            ) {{
                {query_fields}
            }}
        }}
        """
        result = subgraph_post(url, query)
        if result is None:
            print(f"Skipping failed batch at timestamp {current_time}")
            current_time -= 1
            continue

        try:
            data = result["data"][entity]
        except (KeyError, TypeError):
            print(f"Unexpected response at timestamp {current_time}, skipping batch")
            current_time -= 1
            continue

        if not data:
            break

        # Skip records already seen at the boundary of the previous page
        index = 0
        while index < len(data) and data[index]["id"] in last_ids:
            index += 1

        if index == len(data):
            current_time -= 1
            continue

        print(f"{len(data) - index} records found at timestamp {current_time}")
        for item in data[index:]:
            flatten_fn(item)
            records.append(item)

        current_time = int(data[-1]["timestamp"])

        # Track boundary IDs to skip on the next page
        last_ids = set()
        boundary_ts = data[-1]["timestamp"]
        for item in reversed(data):
            if item["timestamp"] == boundary_ts:
                last_ids.add(item["id"])
            else:
                break

    return records


# ---------------------------------------------------------------------------
# Per-entity fetchers
# ---------------------------------------------------------------------------

def fetch_all_transactions(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch all userTransaction records (id, pool, user, timestamp)."""
    url = get_aave_subgraph_url()
    fields = """
        id
        pool { id }
        user { id }
        timestamp
    """
    def flatten(item):
        item["pool"] = item["pool"]["id"]
        item["user"] = item["user"]["id"]
    return _paginate(url, "userTransactions", fields, flatten, start_ts, end_ts)


def fetch_borrows(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch borrow transactions."""
    url = get_aave_subgraph_url()
    fields = """
        id
        user { id }
        caller { id }
        reserve { symbol }
        amount
        borrowRate
        borrowRateMode
        timestamp
        stableTokenDebt
        variableTokenDebt
    """
    def flatten(item):
        item["user"] = item["user"]["id"]
        item["caller"] = item["caller"]["id"]
        item["reserve"] = item["reserve"]["symbol"]
    return _paginate(url, "borrows", fields, flatten, start_ts, end_ts)


def fetch_deposits(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch deposit transactions."""
    url = get_aave_subgraph_url()
    fields = """
        id
        user { id }
        caller { id }
        reserve { symbol }
        amount
        timestamp
    """
    def flatten(item):
        item["user"] = item["user"]["id"]
        item["caller"] = item["caller"]["id"]
        item["reserve"] = item["reserve"]["symbol"]
    return _paginate(url, "deposits", fields, flatten, start_ts, end_ts)


def fetch_repays(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch repay transactions."""
    url = AAVE_LEGACY_URL
    fields = """
        id
        pool { id }
        user { id }
        repayer { id }
        reserve { symbol }
        amount
        timestamp
    """
    def flatten(item):
        item["pool"] = item["pool"]["id"]
        item["user"] = item["user"]["id"]
        item["repayer"] = item["repayer"]["id"]
        item["reserve"] = item["reserve"]["symbol"]
    return _paginate(url, "repays", fields, flatten, start_ts, end_ts)


def fetch_flash_loans(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch flash loan transactions."""
    url = get_aave_subgraph_url()
    fields = """
        id
        reserve { symbol }
        target
        amount
        totalFee
        initiator { id }
        timestamp
    """
    def flatten(item):
        item["initiator"] = item["initiator"]["id"]
        item["reserve"] = item["reserve"]["symbol"]
    return _paginate(url, "flashLoans", fields, flatten, start_ts, end_ts)


def fetch_liquidation_calls(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch liquidation call transactions."""
    url = get_aave_subgraph_url()
    fields = """
        id
        pool { id }
        user { id }
        collateralReserve { symbol }
        collateralAmount
        principalReserve { symbol }
        principalAmount
        liquidator
        timestamp
    """
    def flatten(item):
        item["pool"] = item["pool"]["id"]
        item["user"] = item["user"]["id"]
        item["collateralReserve"] = item["collateralReserve"]["symbol"]
        item["principalReserve"] = item["principalReserve"]["symbol"]
    return _paginate(url, "liquidationCalls", fields, flatten, start_ts, end_ts)


def fetch_redeem_underlyings(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch redeem (withdraw) transactions."""
    url = AAVE_LEGACY_URL
    fields = """
        id
        pool { id }
        user { id }
        to { id }
        reserve { symbol }
        amount
        timestamp
    """
    def flatten(item):
        item["pool"] = item["pool"]["id"]
        item["user"] = item["user"]["id"]
        item["to"] = item["to"]["id"]
        item["reserve"] = item["reserve"]["symbol"]
    return _paginate(url, "redeemUnderlyings", fields, flatten, start_ts, end_ts)


def fetch_swaps(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch borrow rate swap transactions."""
    url = get_aave_subgraph_url()
    fields = """
        id
        pool { id }
        user { id }
        reserve { symbol }
        borrowRateModeFrom
        borrowRateModeTo
        stableBorrowRate
        variableBorrowRate
        timestamp
    """
    def flatten(item):
        item["pool"] = item["pool"]["id"]
        item["user"] = item["user"]["id"]
        item["reserve"] = item["reserve"]["symbol"]
    return _paginate(url, "swaps", fields, flatten, start_ts, end_ts)


def fetch_usage_as_collaterals(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch collateral status change transactions."""
    url = AAVE_LEGACY_URL
    fields = """
        id
        pool { id }
        user { id }
        reserve { symbol }
        fromState
        toState
        timestamp
    """
    def flatten(item):
        item["pool"] = item["pool"]["id"]
        item["user"] = item["user"]["id"]
        item["reserve"] = item["reserve"]["symbol"]
    return _paginate(url, "usageAsCollaterals", fields, flatten, start_ts, end_ts)


def fetch_rebalance_stable_borrow_rates(start_ts=COLLECTION_START_TIMESTAMP, end_ts=COLLECTION_END_TIMESTAMP):
    """Fetch rebalance stable borrow rate transactions."""
    url = AAVE_LEGACY_URL
    fields = """
        id
        pool { id }
        user { id }
        reserve { symbol }
        borrowRateFrom
        borrowRateTo
        timestamp
    """
    def flatten(item):
        item["pool"] = item["pool"]["id"]
        item["user"] = item["user"]["id"]
        item["reserve"] = item["reserve"]["symbol"]
    return _paginate(url, "rebalanceStableBorrowRates", fields, flatten, start_ts, end_ts)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

FETCHER_MAP = {
    "all_transactions":             (fetch_all_transactions,             "allTransaction.csv"),
    "borrow":                       (fetch_borrows,                      "borrow.csv"),
    "deposit":                      (fetch_deposits,                     "deposit.csv"),
    "repay":                        (fetch_repays,                       "repay.csv"),
    "flash_loan":                   (fetch_flash_loans,                  "flashLoan.csv"),
    "liquidation_call":             (fetch_liquidation_calls,            "liquidationCall.csv"),
    "redeem_underlying":            (fetch_redeem_underlyings,           "redeemUnderlying.csv"),
    "swap":                         (fetch_swaps,                        "swap.csv"),
    "usage_as_collateral":          (fetch_usage_as_collaterals,         "usageAsCollateral.csv"),
    "rebalance_stable_borrow_rate": (fetch_rebalance_stable_borrow_rates,"rebalanceStableBorrowRate.csv"),
}


def main():
    parser = argparse.ArgumentParser(description="Fetch AAVE V2 transactions from The Graph")
    parser.add_argument("--type", required=True,
                        choices=list(FETCHER_MAP.keys()) + ["all"],
                        help="Transaction type to fetch, or 'all' for every type")
    parser.add_argument("--start", type=int, default=COLLECTION_START_TIMESTAMP,
                        help="Start Unix timestamp (default: collection start)")
    parser.add_argument("--end", type=int, default=COLLECTION_END_TIMESTAMP,
                        help="End Unix timestamp (default: collection end)")
    args = parser.parse_args()

    targets = list(FETCHER_MAP.items()) if args.type == "all" else [(args.type, FETCHER_MAP[args.type])]

    out_dir = RAW_DIR / "transactions"
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, (fetch_fn, filename) in targets:
        print(f"\n=== Fetching {name} ===")
        records = fetch_fn(start_ts=args.start, end_ts=args.end)
        if not records:
            print(f"No records fetched for {name}")
            continue
        out_path = out_dir / filename
        fieldnames = list(records[0].keys())
        write_csv(out_path, fieldnames, records)
        print(f"Wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
