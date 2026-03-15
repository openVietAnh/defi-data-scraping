"""Fetch token price history and USD/ETH price history from AAVE V2 subgraph.

Usage:
    python -m src.fetchers.prices --type token_eth --token DAI
    python -m src.fetchers.prices --type usd_eth
    python -m src.fetchers.prices --type reserves
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import AAVE_LEGACY_URL, TOKENS, COLLECTION_START_TIMESTAMP, RAW_DIR
from src.fetchers.base import subgraph_post
from src.utils.csv_io import write_csv


def fetch_token_price_in_eth(token: str, start_ts: int = COLLECTION_START_TIMESTAMP) -> list:
    """Fetch historical price of a token denominated in ETH."""
    prices = []
    current_time = start_ts

    while True:
        query = f"""
        {{
            reserves(where: {{symbol: "{token}"}}) {{
                price {{
                    priceHistory(
                        where: {{timestamp_lt: {current_time}}},
                        first: 1000,
                        orderBy: timestamp,
                        orderDirection: desc
                    ) {{
                        price
                        timestamp
                    }}
                }}
            }}
        }}
        """
        result = subgraph_post(AAVE_LEGACY_URL, query)
        if result is None:
            print(f"Skipping failed batch at timestamp {current_time}")
            continue

        try:
            data = result["data"]["reserves"][0]["price"]["priceHistory"]
        except (KeyError, IndexError, TypeError) as exc:
            print(f"Unexpected response at timestamp {current_time}: {exc}")
            continue

        if not data:
            break

        print(f"{len(data)} prices found at timestamp {current_time}")
        prices.extend(data)
        current_time = int(data[-1]["timestamp"])

    return prices


def fetch_usd_eth_price(start_ts: int = COLLECTION_START_TIMESTAMP) -> list:
    """Fetch historical USD/ETH price from AAVE V2 subgraph."""
    prices = []
    current_time = start_ts

    while True:
        query = f"""
        {{
            usdEthPriceHistoryItems(
                first: 1000,
                where: {{timestamp_lt: {current_time}}},
                orderBy: timestamp,
                orderDirection: desc
            ) {{
                timestamp
                price
            }}
        }}
        """
        result = subgraph_post(AAVE_LEGACY_URL, query)
        if result is None:
            print(f"Skipping failed batch at timestamp {current_time}")
            continue

        try:
            data = result["data"]["usdEthPriceHistoryItems"]
        except (KeyError, TypeError) as exc:
            print(f"Unexpected response at timestamp {current_time}: {exc}")
            continue

        if not data:
            break

        print(f"{len(data)} rows found at timestamp {current_time}")
        prices.extend(data)
        current_time = int(data[-1]["timestamp"])

    return prices


def fetch_reserves() -> list:
    """Fetch the list of AAVE V2 reserve names and symbols."""
    query = """
    {
        reserves {
            id
            name
            symbol
        }
    }
    """
    result = subgraph_post(AAVE_LEGACY_URL, query)
    if result is None:
        return []
    return result.get("data", {}).get("reserves", [])


def main():
    parser = argparse.ArgumentParser(description="Fetch AAVE V2 price data")
    parser.add_argument("--type", required=True,
                        choices=["token_eth", "usd_eth", "reserves"],
                        help="Which price data to fetch")
    parser.add_argument("--token", choices=TOKENS,
                        help="Required for --type token_eth")
    parser.add_argument("--start", type=int, default=COLLECTION_START_TIMESTAMP,
                        help="Start Unix timestamp")
    args = parser.parse_args()

    raw_prices_dir = RAW_DIR / "prices"
    raw_prices_dir.mkdir(parents=True, exist_ok=True)

    if args.type == "token_eth":
        if not args.token:
            print("--token is required for --type token_eth")
            sys.exit(1)
        records = fetch_token_price_in_eth(args.token, args.start)
        out_path = raw_prices_dir / f"{args.token}_price_in_eth.csv"
        write_csv(out_path, ["timestamp", "price"], records)
        print(f"Wrote {len(records)} records to {out_path}")

    elif args.type == "usd_eth":
        records = fetch_usd_eth_price(args.start)
        out_path = raw_prices_dir / "usd_eth_full.csv"
        write_csv(out_path, ["timestamp", "price"], records)
        print(f"Wrote {len(records)} records to {out_path}")

    elif args.type == "reserves":
        records = fetch_reserves()
        out_path = raw_prices_dir / "reserves.csv"
        write_csv(out_path, ["id", "name", "symbol"], records)
        print(f"Wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
