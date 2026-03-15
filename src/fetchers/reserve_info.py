"""Fetch historical reserve info (rates, TVL) from AAVE V2 subgraph.

Reads a file of block numbers and fetches reserve data for all blocks,
batching up to 50 blocks per GraphQL request to minimize round-trips.

Usage:
    python -m src.fetchers.reserve_info --token DAI
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import get_aave_subgraph_url, TOKENS, RAW_DIR
from src.fetchers.base import subgraph_post
from src.utils.csv_io import write_csv

BATCH_SIZE = 50  # blocks per GraphQL query (was 10; 50 cuts requests by 5×)

OUTPUT_KEYS = [
    "decimals", "totalDeposits", "stableBorrowRate", "variableBorrowRate",
    "liquidityRate", "utilizationRate", "lastUpdateTimestamp", "blockNumber",
]


def fetch_reserve_info(token: str, blocks_path: Path) -> list:
    """Fetch reserve info for every block number listed in blocks_path.

    Returns a list of dicts with one entry per block.
    """
    url = get_aave_subgraph_url()

    with open(blocks_path) as f:
        block_numbers = [line.strip() for line in f if line.strip()]

    records = []
    errors = []
    total = len(block_numbers)

    for batch_start in range(0, total, BATCH_SIZE):
        batch = block_numbers[batch_start: batch_start + BATCH_SIZE]

        # Build a multi-alias query: one field alias per block
        aliases = ""
        for num in batch:
            aliases += f"""
            b{num}: reserves(block: {{number: {num}}}, where: {{symbol: "{token}"}}) {{
                decimals
                totalDeposits
                stableBorrowRate
                variableBorrowRate
                liquidityRate
                utilizationRate
                lastUpdateTimestamp
            }}
            """
        query = "{\n" + aliases + "\n}"

        result = subgraph_post(url, query)
        if result is None:
            print(f"Failed batch ending at block {batch[-1]}, recording as errors")
            errors.extend(batch)
            continue

        data = result.get("data", {})
        for num in batch:
            key = f"b{num}"
            block_data_list = data.get(key)
            if not block_data_list:
                errors.append(num)
                continue
            block_data = block_data_list[0]
            block_data["blockNumber"] = num
            records.append(block_data)

        done = min(batch_start + BATCH_SIZE, total)
        print(f"{done}/{total} blocks fetched ({done / total * 100:.1f}%)")

    if errors:
        print(f"Failed to fetch {len(errors)} blocks: {errors[:10]}{'...' if len(errors) > 10 else ''}")

    return records


def main():
    parser = argparse.ArgumentParser(description="Fetch AAVE V2 reserve info per block")
    parser.add_argument("--token", required=True, choices=TOKENS,
                        help="Token symbol to fetch (e.g. DAI)")
    parser.add_argument("--blocks", type=Path,
                        help="Path to file of block numbers (one per line). "
                             "Defaults to data/raw/reserve_info/<TOKEN>.txt")
    args = parser.parse_args()

    blocks_path = args.blocks or (RAW_DIR / "reserve_info" / f"{args.token}.txt")
    if not blocks_path.exists():
        print(f"Block list not found: {blocks_path}")
        sys.exit(1)

    records = fetch_reserve_info(args.token, blocks_path)
    if not records:
        print("No records fetched.")
        sys.exit(1)

    out_path = RAW_DIR / "reserve_info" / f"{args.token}_info.csv"
    write_csv(out_path, OUTPUT_KEYS, records)
    print(f"Wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
