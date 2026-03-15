"""Generate fixed-interval time-series snapshots via forward-fill.

Reads the full reserve info for each token and emits one row per
interval (default 5 minutes) by carrying forward the most recent known
values until the next observed data point.

Usage:
    python -m src.aggregators.timeseries --interval 5
    python -m src.aggregators.timeseries --interval 60
"""

import argparse
import csv
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import TOKENS, PROCESSED_DIR, OUTPUT_DIR

SNAPSHOT_KEYS = [
    "timestamp", "time", "blockNumber",
    "totalDeposits", "depositRate",
    "stableBorrowRate", "variableBorrowRate", "utilizationRate",
    "userCount", "HHI", "depositers", "borrowers", "price",
]

# Per-token data collection windows (start, end as datetime)
TOKEN_WINDOWS = {
    "DAI":  (datetime.datetime(2020, 12, 1, 23, 40, 50),  datetime.datetime(2022, 7, 31, 23, 12, 24)),
    "USDC": (datetime.datetime(2020, 12, 2, 20, 7, 35),   datetime.datetime(2022, 7, 31, 23, 12, 24)),
    "USDT": (datetime.datetime(2020, 12, 2, 17, 15, 31),  datetime.datetime(2022, 7, 31, 23, 12, 24)),
    "WBTC": (datetime.datetime(2020, 12, 2, 19, 55, 51),  datetime.datetime(2022, 7, 31, 23, 12, 24)),
    "WETH": (datetime.datetime(2020, 12, 1, 6, 11, 40),   datetime.datetime(2022, 7, 31, 23, 12, 24)),
}


def generate_timeseries(token: str, full_info_path: Path, out_path: Path,
                         interval_minutes: int = 5) -> None:
    """Forward-fill full_info records to produce a regular time-series CSV.

    For each interval tick between start_time and end_time, the most
    recently seen data row is carried forward and emitted at the tick's
    timestamp.
    """
    start_time, end_time = TOKEN_WINDOWS.get(
        token, (datetime.datetime(2020, 12, 2, 20, 8), datetime.datetime(2022, 7, 31, 23, 12))
    )
    delta = datetime.timedelta(minutes=interval_minutes)

    data = []
    time_cursor = start_time
    info = None  # most recently seen data row

    with open(full_info_path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            new_info = {SNAPSHOT_KEYS[i]: item[i] for i in range(len(item))}
            row_time = datetime.datetime.fromtimestamp(int(item[0]))

            if row_time < time_cursor:
                info = new_info
                continue

            # Emit one snapshot per interval tick up to row_time
            while time_cursor <= row_time and time_cursor <= end_time:
                if info is not None:
                    info["timestamp"] = int(time_cursor.timestamp())
                    info["time"] = (f"{time_cursor.day}/{time_cursor.month}/"
                                    f"{time_cursor.year} "
                                    f"{time_cursor.hour}:{time_cursor.minute:02d}")
                    data.append(dict(info))
                time_cursor += delta

            info = new_info
            if row_time > end_time:
                break

    # Emit one final row if we still have data
    if info is not None and time_cursor <= end_time:
        info["timestamp"] = int(time_cursor.timestamp())
        info["time"] = (f"{time_cursor.day}/{time_cursor.month}/"
                        f"{time_cursor.year} "
                        f"{time_cursor.hour}:{time_cursor.minute:02d}")
        data.append(dict(info))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SNAPSHOT_KEYS)
        writer.writeheader()
        writer.writerows(data)

    print(f"[timeseries] {token} {interval_minutes}min: {len(data)} rows → {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate fixed-interval time-series")
    parser.add_argument("--interval", type=int, default=5,
                        help="Interval in minutes (default: 5)")
    parser.add_argument("--token", choices=TOKENS,
                        help="Token to process (omit for all tokens)")
    args = parser.parse_args()

    tokens = [args.token] if args.token else TOKENS
    label = f"{args.interval}min" if args.interval != 60 else "1hour"

    for token in tokens:
        full_info_path = PROCESSED_DIR / "reserve_info" / f"{token}_full_info.csv"
        if not full_info_path.exists():
            print(f"[timeseries] Skipping {token}: {full_info_path} not found")
            continue
        out_path = OUTPUT_DIR / label / f"{token}.csv"
        generate_timeseries(token, full_info_path, out_path, args.interval)


if __name__ == "__main__":
    main()
