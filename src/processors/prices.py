"""Process raw price data: merge, sort, deduplicate, and convert to USD.

Pipeline stages (run in order):
    1. merge_usd_eth    — merge raw USD/ETH price chunk files into one
    2. sort_usd_eth     — sort the merged file by timestamp
    3. dedup_usd_eth    — remove duplicate timestamps
    4. fill_missing_eth — interpolate missing ETH prices for needed timestamps
    5. convert_to_usd   — convert token-in-ETH prices to token-in-USD
    6. convert_weth     — derive WETH USD price from USD/ETH price

Usage:
    python -m src.processors.prices --stage all
"""

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import TOKENS, PROCESSED_DIR, RAW_DIR
from src.fetchers.base import subgraph_post
from config import AAVE_LEGACY_URL
from src.utils.csv_io import write_csv

ETH_PRICE_FILENAME = "usd_eth_full_updated.csv"
ETH_18_DECIMALS = 10 ** 18


# ---------------------------------------------------------------------------
# Stage 1: Merge raw USD/ETH chunk files
# ---------------------------------------------------------------------------

def merge_usd_eth(raw_price_dir: Path, out_dir: Path) -> None:
    """Merge multiple raw USD/ETH price chunk files (0.csv, 1.csv …) into one."""
    seen = set()
    prices = []
    i = 0
    while True:
        path = raw_price_dir / f"{i}.csv"
        if not path.exists():
            break
        with open(path, newline="") as f:
            for row in csv.reader(f):
                if row[1] not in seen:
                    prices.append({"price": row[0], "timestamp": row[1]})
                    seen.add(row[1])
        i += 1

    out_path = out_dir / "usd_eth_prices.csv"
    write_csv(out_path, ["price", "timestamp"], prices)
    print(f"[merge_usd_eth] {len(prices)} unique prices → {out_path}")


# ---------------------------------------------------------------------------
# Stage 2 & 3: Sort + deduplicate USD/ETH price file
# ---------------------------------------------------------------------------

def sort_and_dedup_usd_eth(price_path: Path) -> None:
    """Sort the USD/ETH price file by timestamp and remove duplicates."""
    seen = set()
    prices = []
    with open(price_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0] not in seen:
                prices.append({"timestamp": row[0], "price": row[1]})
                seen.add(row[0])

    prices.sort(key=lambda x: x["timestamp"])
    write_csv(price_path, ["timestamp", "price"], prices)
    print(f"[sort_dedup] {price_path.name}: {len(prices)} rows")


# ---------------------------------------------------------------------------
# Stage 4: Fill missing ETH prices by linear interpolation
# ---------------------------------------------------------------------------

def _interpolate_price(time: int, before_ts: int, before_price: int,
                        after_ts: int, after_price: int) -> float:
    """Linearly interpolate a price between two known data points."""
    time_diff = after_ts - before_ts
    price_diff = after_price - before_price
    return before_price + (price_diff / time_diff) * (time - before_ts)


def fill_missing_eth_prices(eth_price_path: Path, processed_info_dir: Path,
                             tokens: list, out_path: Path) -> None:
    """Fetch and interpolate ETH prices for any timestamps missing from the price file."""
    timestamp_to_price = {}
    with open(eth_price_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            timestamp_to_price[int(row[0])] = int(row[1])

    time_list = sorted(timestamp_to_price.keys())

    needed_timestamps = set()
    for token in tokens:
        path = processed_info_dir / f"{token}_processed_info.csv"
        if not path.exists():
            continue
        with open(path, newline="") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                ts = int(row[0])
                if ts not in timestamp_to_price:
                    needed_timestamps.add(ts)

    for ts in needed_timestamps:
        if ts < time_list[0]:
            timestamp_to_price[ts] = timestamp_to_price[time_list[0]]
            continue
        if ts > time_list[-1]:
            timestamp_to_price[ts] = timestamp_to_price[time_list[-1]]
            continue

        # Binary search for surrounding prices
        lo, hi = 0, len(time_list) - 2
        while lo < hi:
            mid = (lo + hi) // 2
            if time_list[mid] <= ts <= time_list[mid + 1]:
                lo = mid
                break
            elif ts < time_list[mid]:
                hi = mid - 1
            else:
                lo = mid + 1

        price = _interpolate_price(
            ts,
            time_list[lo], timestamp_to_price[time_list[lo]],
            time_list[lo + 1], timestamp_to_price[time_list[lo + 1]],
        )
        timestamp_to_price[ts] = int(price)

    records = [{"timestamp": ts, "price": p} for ts, p in sorted(timestamp_to_price.items())]
    write_csv(out_path, ["timestamp", "price"], records)
    print(f"[fill_missing_eth] Wrote {len(records)} prices to {out_path}")


# ---------------------------------------------------------------------------
# Stage 5: Convert token price in ETH → USD
# ---------------------------------------------------------------------------

def convert_to_usd(token: str, eth_price_in_token_path: Path,
                   usd_eth_path: Path, out_path: Path) -> None:
    """Derive USD price for a token from its ETH price and the USD/ETH rate."""
    usd_per_eth = {}
    with open(usd_eth_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            usd_per_eth[row[0]] = row[1]

    records = []
    with open(eth_price_in_token_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            # WBTC prices are stored with fewer digits; pad to 20 digits
            if token == "WBTC":
                eth_price = int(row[1]) * (10 ** max(0, 20 - len(row[1])))
            else:
                eth_price = int(row[1])
            usd_eth = usd_per_eth.get(row[0])
            if usd_eth:
                usd_price = eth_price / float(usd_eth)
                records.append({"timestamp": row[0], "price": usd_price})

    write_csv(out_path, ["timestamp", "price"], records)
    print(f"[convert_to_usd] {token}: {len(records)} prices → {out_path}")


# ---------------------------------------------------------------------------
# Stage 6: Derive WETH USD price from USD/ETH price
# ---------------------------------------------------------------------------

def convert_weth_price(usd_eth_path: Path, out_path: Path) -> None:
    """Compute WETH USD price as 1 / (usdEthPrice / 10^18)."""
    records = []
    with open(usd_eth_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            usd_price = 1 / (float(row[1]) / ETH_18_DECIMALS)
            records.append({"timestamp": row[0], "price": usd_price})

    write_csv(out_path, ["timestamp", "price"], records)
    print(f"[convert_weth] {len(records)} WETH prices → {out_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Process price data")
    parser.add_argument("--stage", required=True,
                        choices=["merge_usd_eth", "sort_dedup", "fill_missing",
                                 "convert_to_usd", "convert_weth", "all"],
                        help="Stage to run")
    args = parser.parse_args()

    raw_price_dir = RAW_DIR / "prices"
    processed_price_dir = PROCESSED_DIR / "prices"
    processed_reserve_dir = PROCESSED_DIR / "reserve_info"
    processed_price_dir.mkdir(parents=True, exist_ok=True)

    eth_price_path = processed_price_dir / ETH_PRICE_FILENAME
    non_weth_tokens = [t for t in TOKENS if t != "WETH"]

    if args.stage in ("merge_usd_eth", "all"):
        merge_usd_eth(raw_price_dir, processed_price_dir)

    if args.stage in ("sort_dedup", "all"):
        prices_csv = processed_price_dir / "usd_eth_prices.csv"
        if prices_csv.exists():
            sort_and_dedup_usd_eth(prices_csv)

    if args.stage in ("fill_missing", "all"):
        fill_missing_eth_prices(
            eth_price_path=processed_price_dir / "usd_eth_prices.csv",
            processed_info_dir=processed_reserve_dir,
            tokens=non_weth_tokens,
            out_path=eth_price_path,
        )

    if args.stage in ("convert_to_usd", "all"):
        for token in non_weth_tokens:
            eth_token_path = raw_price_dir / f"{token}_price_in_eth.csv"
            if eth_token_path.exists():
                convert_to_usd(
                    token,
                    eth_price_in_token_path=eth_token_path,
                    usd_eth_path=eth_price_path,
                    out_path=processed_price_dir / f"{token}-usd-price.csv",
                )

    if args.stage in ("convert_weth", "all"):
        convert_weth_price(
            usd_eth_path=eth_price_path,
            out_path=processed_price_dir / "WETH-usd-price.csv",
        )


if __name__ == "__main__":
    main()
