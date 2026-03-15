"""Fetch Compound V2 daily financial snapshots from The Graph.

Writes: compound.csv
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.fetchers.base import subgraph_post

BASE = Path(__file__).parent
URL = "https://gateway.thegraph.com/api/[API_KEY]/subgraphs/id/6tGbL7WBx287EZwGUvvcQdL6m67JGMJrma3JSTtt5SV7"

QUERY = """
{
    financialsDailySnapshots(first: 1000, orderBy: timestamp, orderDirection: asc) {
        timestamp
        totalValueLockedUSD
        totalDepositBalanceUSD
        totalBorrowBalanceUSD
    }
}
"""

KEYS = ["timestamp", "totalBorrowBalanceUSD", "totalValueLockedUSD", "totalDepositBalanceUSD"]


def main():
    result = subgraph_post(URL, QUERY)
    if result is None:
        print("Failed to fetch Compound V2 data")
        return

    try:
        data = result["data"]["financialsDailySnapshots"]
    except (KeyError, TypeError) as exc:
        print(f"Unexpected response: {exc}")
        return

    rows = [{k: item[k] for k in KEYS} for item in data]
    out_path = BASE / "compound.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=KEYS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
