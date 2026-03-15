"""Fetch daily Compound DAI snapshots from The Graph subgraph.

Writes: dai.csv
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.fetchers.base import subgraph_post

BASE = Path(__file__).parent
URL = "https://gateway.thegraph.com/api/[API_KEY]/subgraphs/id/6tGbL7WBx287EZwGUvvcQdL6m67JGMJrma3JSTtt5SV7"
KEYS = ["timestamp", "totalBorrowBalanceUSD", "totalValueLockedUSD"]


def fetch_compound_dai(current_time: int = 1574984855) -> list:
    records = []
    while True:
        query = f"""
        {{
            marketDailySnapshots(where: {{market_: {{name: "Compound Dai"}}}}) {{
                market {{
                    dailySnapshots(
                        first: 1000,
                        orderBy: timestamp,
                        orderDirection: asc,
                        where: {{ timestamp_gt: {current_time} }}
                    ) {{
                        timestamp
                        totalBorrowBalanceUSD
                        totalValueLockedUSD
                    }}
                }}
            }}
        }}
        """
        result = subgraph_post(URL, query)
        if result is None:
            continue
        try:
            data = (result["data"]["marketDailySnapshots"]
                    ["market"]["dailySnapshots"])
        except (KeyError, TypeError) as exc:
            print(f"Unexpected response at timestamp {current_time}: {exc}")
            continue
        if not data:
            break
        print(f"{len(data)} rows found at timestamp {current_time}")
        records.extend(data)
        current_time = int(data[-1]["timestamp"])
    return records


def main():
    records = fetch_compound_dai()
    out_path = BASE / "dai.csv"
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=KEYS)
        writer.writeheader()
        writer.writerows(records)
    print(f"Wrote {len(records)} rows to {out_path}")


if __name__ == "__main__":
    main()
