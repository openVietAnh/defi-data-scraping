"""Process raw AAVE V2 reserve info through each pipeline stage.

Pipeline stages (run in order):
    1. process_raw      — decimal conversion + APY calculation
    2. calc_market_size — multiply total deposits by USD price
    3. add_prices       — attach USD price column to reserve info
    4. merge_user_data  — merge userCount, HHI, depositors, borrowers

Usage:
    python -m src.processors.reserve --stage process_raw
    python -m src.processors.reserve --stage all
"""

import argparse
import csv
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import TOKENS, TOKEN_DECIMALS, SECONDS_PER_YEAR, RAY, PROCESSED_DIR
from src.utils.csv_io import write_csv


# ---------------------------------------------------------------------------
# Stage 1: Raw → processed info (decimal conversion + APY)
# ---------------------------------------------------------------------------

def liquidity_rate_to_apy(liquidity_rate: int) -> float:
    """Convert an AAVE V2 liquidityRate (ray units) to annual percentage yield.

    Formula: (1 + rate / RAY / SECONDS_PER_YEAR) ** SECONDS_PER_YEAR - 1
    """
    return (1 + liquidity_rate / RAY / SECONDS_PER_YEAR) ** SECONDS_PER_YEAR - 1


PROCESSED_KEYS = [
    "timestamp", "time", "blockNumber",
    "totalDeposits", "depositRate",
    "stableBorrowRate", "variableBorrowRate", "utilizationRate",
]


def process_raw(token: str, raw_path: Path, out_path: Path) -> None:
    """Convert raw subgraph reserve data to human-readable values.

    - totalDeposits: divide by 10^decimals
    - stableBorrowRate / variableBorrowRate: divide by 10^25
    - depositRate: convert liquidityRate from ray to APY
    - timestamp: add ISO datetime column
    """
    decimals = TOKEN_DECIMALS[token]
    records = []

    with open(raw_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for item in reader:
            records.append({
                "totalDeposits":    int(item[1]) / (10 ** decimals),
                "stableBorrowRate": int(item[2]) / (10 ** 25),
                "variableBorrowRate": int(item[3]) / (10 ** 25),
                "depositRate":      liquidity_rate_to_apy(int(item[4])),
                "utilizationRate":  item[5],
                "timestamp":        item[6],
                "blockNumber":      item[7],
                "time": datetime.datetime.fromtimestamp(int(item[6])).isoformat(),
            })

    records.sort(key=lambda x: x["timestamp"])
    write_csv(out_path, PROCESSED_KEYS, records)
    print(f"[process_raw] {token}: {len(records)} records → {out_path}")


# ---------------------------------------------------------------------------
# Stage 2: Multiply totalDeposits by USD price → TLV in USD
# ---------------------------------------------------------------------------

def calc_market_size_usd(token: str, processed_path: Path, price_path: Path, out_path: Path) -> None:
    """Multiply totalDeposits by the token's USD price to get market size in USD."""
    token_prices = {}
    with open(price_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            token_prices[item[0]] = float(item[1])

    records = []
    with open(processed_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            row = {PROCESSED_KEYS[i]: item[i] for i in range(len(PROCESSED_KEYS))}
            row["totalDeposits"] = float(row["totalDeposits"]) * token_prices[item[0]]
            records.append(row)

    write_csv(out_path, PROCESSED_KEYS, records)
    print(f"[calc_market_size_usd] {token}: {len(records)} records → {out_path}")


# ---------------------------------------------------------------------------
# Stage 3: Attach USD price column to reserve info
# ---------------------------------------------------------------------------

FULL_INFO_KEYS = PROCESSED_KEYS + ["userCount", "HHI", "depositers", "borrowers", "price"]


def add_prices(token: str, info_path: Path, price_path: Path, out_path: Path) -> None:
    """Append a USD price column to the merged reserve info file."""
    prices = {}
    with open(price_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            prices[item[0]] = float(item[1])

    info_keys = PROCESSED_KEYS + ["userCount", "HHI", "depositers", "borrowers"]
    records = []
    with open(info_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            row = {info_keys[i]: item[i] for i in range(len(info_keys))}
            row["price"] = prices[item[0]]
            records.append(row)

    write_csv(out_path, FULL_INFO_KEYS, records)
    print(f"[add_prices] {token}: {len(records)} records → {out_path}")


# ---------------------------------------------------------------------------
# Stage 4: Merge userCount, HHI, depositors, borrowers into reserve info
# ---------------------------------------------------------------------------

def merge_user_data(token: str, tlv_path: Path, user_count_path: Path,
                    depositors_path: Path, borrowers_path: Path, out_path: Path) -> None:
    """Merge user count, HHI, depositor count, and borrower count into reserve data.

    Uses forward-fill for blocks without a matching user count record.
    """
    user_count = {}
    with open(user_count_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            user_count[item[0]] = item[1]

    hhi = {}
    depositors = {}
    with open(depositors_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            hhi[item[0]] = item[1]
            depositors[item[0]] = item[2]

    borrowers = {}
    with open(borrowers_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            borrowers[item[0]] = item[1]

    base_keys = PROCESSED_KEYS
    last_user_count = last_hhi = last_depositors = last_borrowers = 0
    records = []

    with open(tlv_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            row = {base_keys[i]: item[i] for i in range(len(base_keys))}
            ts = item[0]
            block = item[2]

            if ts in user_count:
                last_user_count = user_count[ts]
            row["userCount"] = last_user_count

            if block in hhi:
                last_hhi = hhi[block]
            row["HHI"] = last_hhi

            if block in depositors:
                last_depositors = depositors[block]
            row["depositers"] = last_depositors

            if block in borrowers:
                last_borrowers = borrowers[block]
            row["borrowers"] = last_borrowers

            records.append(row)

    merged_keys = base_keys + ["userCount", "HHI", "depositers", "borrowers"]
    write_csv(out_path, merged_keys, records)
    print(f"[merge_user_data] {token}: {len(records)} records → {out_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Process AAVE V2 reserve info")
    parser.add_argument("--stage", required=True,
                        choices=["process_raw", "calc_market_size", "add_prices",
                                 "merge_user_data", "all"],
                        help="Processing stage to run")
    parser.add_argument("--token", choices=TOKENS,
                        help="Token to process (omit to run for all tokens)")
    args = parser.parse_args()

    tokens = [args.token] if args.token else TOKENS
    raw_dir = PROCESSED_DIR / "reserve_info"
    price_dir = PROCESSED_DIR / "token_price_usd"
    user_count_dir = PROCESSED_DIR / "token_user_count"
    depositors_dir = PROCESSED_DIR / "depositors"
    borrowers_dir = PROCESSED_DIR / "borrowers"

    for token in tokens:
        if args.stage in ("process_raw", "all"):
            process_raw(
                token,
                raw_path=PROCESSED_DIR.parent / "raw" / "reserve_info" / f"{token}_info.csv",
                out_path=raw_dir / f"{token}_processed_info.csv",
            )
        if args.stage in ("calc_market_size", "all"):
            calc_market_size_usd(
                token,
                processed_path=raw_dir / f"{token}_processed_info.csv",
                price_path=price_dir / f"{token}-usd-price.csv",
                out_path=raw_dir / f"{token}_TLV_USD.csv",
            )
        if args.stage in ("merge_user_data", "all"):
            merge_user_data(
                token,
                tlv_path=raw_dir / f"{token}_TLV_USD.csv",
                user_count_path=user_count_dir / f"{token}.csv",
                depositors_path=depositors_dir / f"{token}_depositers.csv",
                borrowers_path=borrowers_dir / f"{token}_borrowers.csv",
                out_path=raw_dir / f"{token}_info.csv",
            )
        if args.stage in ("add_prices", "all"):
            add_prices(
                token,
                info_path=raw_dir / f"{token}_info.csv",
                price_path=price_dir / f"{token}-usd-price.csv",
                out_path=raw_dir / f"{token}_full_info.csv",
            )


if __name__ == "__main__":
    main()
