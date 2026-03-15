"""Merge MakerDAO protocol-level metrics into one CSV.

Reads: fee-revenue.csv, market-cap.csv, price.csv, tvl-borrow.csv
Writes: makerDAO-RQ2.csv
"""

import csv
from pathlib import Path

BASE = Path(__file__).parent


def _get(mapping: dict, key: str, index: int, default: str = "TBD") -> str:
    entry = mapping.get(key)
    if entry is None or index >= len(entry):
        return default
    return entry[index]


def load_two_col(path: Path, key_col: int, *val_cols: int) -> dict:
    result = {}
    with open(path, newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            result[row[key_col]] = tuple(row[c] for c in val_cols)
    return result


def main():
    fee_rev = load_two_col(BASE / "fee-revenue.csv", 0, 1, 2)
    market_cap = load_two_col(BASE / "market-cap.csv", 0, 1, 2)
    prices = load_two_col(BASE / "price.csv", 0, 1)

    data = []
    with open(BASE / "tvl-borrow.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            date = row[0]
            deposit = float(row[1])
            borrow = float(row[2])
            record = {
                "Date":               date,
                "Total Deposit":      deposit,
                "Total Borrowed":     borrow,
                "Utilization Rate":   borrow / deposit if deposit else 0,
                "Liquidity":          deposit - borrow,
                "Fee":                _get(fee_rev, date, 0),
                "Revenue":            _get(fee_rev, date, 1),
                "Fully Diluted Market Cap": _get(market_cap, date, 0),
                "Circulating Market Cap":   _get(market_cap, date, 1),
                "Price":              _get(prices, date, 0),
            }
            data.append(record)

    keys = list(data[0].keys())
    out_path = BASE / "makerDAO-RQ2.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Wrote {len(data)} rows to {out_path}")


if __name__ == "__main__":
    main()
