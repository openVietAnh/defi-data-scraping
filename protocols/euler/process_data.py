"""Process Euler protocol daily snapshot data.

Reads:  euler.csv
Writes: euler_info.csv
"""

import csv
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).parent
KEYS = ["date", "totalBorrow", "totalValueLocked", "utilizationRate", "liquidity"]


def main():
    rows = []
    with open(BASE / "euler.csv", newline="") as f:
        reader = csv.reader(f)
        next(reader)
        for item in reader:
            tvl = float(item[2])
            borrow = float(item[1])
            rows.append({
                "date":             datetime.fromtimestamp(int(item[0])).strftime("%d/%m/%Y"),
                "totalBorrow":      borrow,
                "totalValueLocked": tvl,
                "utilizationRate":  borrow / tvl if tvl else 0,
                "liquidity":        tvl - borrow,
            })

    out_path = BASE / "euler_info.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=KEYS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
