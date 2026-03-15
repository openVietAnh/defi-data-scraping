"""Compute daily averages from the 5-minute time-series data.

For each day, averages all numeric columns across the intraday snapshots.

Usage:
    python -m src.aggregators.averages --token DAI
    python -m src.aggregators.averages              # all tokens
"""

import argparse
import csv
import datetime
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import TOKENS, OUTPUT_DIR

NUMERIC_KEYS = [
    "totalDeposits", "depositRate", "stableBorrowRate", "variableBorrowRate",
    "utilizationRate", "userCount", "HHI", "depositers", "borrowers", "price",
]

OUTPUT_KEYS = ["date"] + NUMERIC_KEYS


def compute_daily_averages(token: str, timeseries_path: Path, out_path: Path) -> None:
    """Average all numeric columns by calendar day."""
    daily = defaultdict(lambda: defaultdict(list))
    start_date = datetime.datetime(2020, 12, 2)

    with open(timeseries_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            ts = int(item[0])
            dt = datetime.datetime.fromtimestamp(ts)
            if dt < start_date:
                continue
            day = datetime.datetime(dt.year, dt.month, dt.day)
            for key, val in zip(NUMERIC_KEYS, item[3:]):  # skip timestamp, time, blockNumber
                try:
                    daily[day][key].append(float(val))
                except ValueError:
                    pass

    records = []
    day = start_date
    while day in daily:
        row = {"date": day.strftime("%d/%m/%Y")}
        for key in NUMERIC_KEYS:
            values = daily[day][key]
            row[key] = sum(values) / len(values) if values else 0
        records.append(row)
        day += datetime.timedelta(days=1)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_KEYS)
        writer.writeheader()
        writer.writerows(records)

    print(f"[averages] {token}: {len(records)} daily rows → {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Compute daily averages from 5-min snapshots")
    parser.add_argument("--token", choices=TOKENS,
                        help="Token to process (omit for all tokens)")
    args = parser.parse_args()

    tokens = [args.token] if args.token else TOKENS
    for token in tokens:
        timeseries_path = OUTPUT_DIR / "5min" / f"{token}.csv"
        if not timeseries_path.exists():
            print(f"[averages] Skipping {token}: {timeseries_path} not found")
            continue
        out_path = OUTPUT_DIR / "daily" / f"{token}_average.csv"
        compute_daily_averages(token, timeseries_path, out_path)


if __name__ == "__main__":
    main()
