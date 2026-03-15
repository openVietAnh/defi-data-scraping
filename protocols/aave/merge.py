"""Merge AAVE protocol-level metrics (TVL, fees, market cap) into one CSV.

Reads: fee-revenue.csv, market-cap.csv, price.csv, tvl-borrow.csv
Writes: aave-RQ2.csv
"""

import csv
from pathlib import Path

BASE = Path(__file__).parent


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
            deposit, borrow = float(row[1]), float(row[2])
            record = {
                "Date":               date,
                "Total Deposit":      deposit,
                "Total Borrowed":     borrow,
                "Utilization Rate":   borrow / deposit if deposit else 0,
                "Liquidity":          deposit - borrow,
                "Fee":                fee_rev.get(date, ("TBD",))[0],
                "Revenue":            fee_rev.get(date, ("TBD", "TBD"))[1],
                "Fully Diluted Market Cap": market_cap.get(date, ("TBD",))[0],
                "Circulating Market Cap":   market_cap.get(date, ("TBD", "TBD"))[1],
                "Price":              prices.get(date, ("TBD",))[0],
            }
            data.append(record)

    keys = list(data[0].keys())
    out_path = BASE / "aave-RQ2.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)
    print(f"Wrote {len(data)} rows to {out_path}")


if __name__ == "__main__":
    main()
