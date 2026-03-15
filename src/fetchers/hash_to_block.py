"""Resolve transaction hashes to Ethereum block numbers using the Alchemy node.

Reads per-token filtered hash files and writes a CSV mapping hash → block.

Usage:
    python -m src.fetchers.hash_to_block
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from web3 import Web3

from config import get_alchemy_url, TOKENS, PROCESSED_DIR
from src.utils.csv_io import write_csv


def load_hashes(tokens: list, processed_dir: Path) -> set:
    """Load all unique transaction hashes from per-token filtered hash files."""
    hash_set = set()
    for token in tokens:
        path = processed_dir / "hash_to_block" / f"{token}_filtered.csv"
        if not path.exists():
            print(f"Hash file not found, skipping: {path}")
            continue
        with open(path) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header if present
            for row in reader:
                if row:
                    hash_set.add(row[0])
    return hash_set


def resolve_hashes(hash_set: set, web3: Web3) -> list:
    """Resolve each tx hash to a block number via the Alchemy node."""
    records = []
    total = len(hash_set)
    for i, tx_hash in enumerate(hash_set, 1):
        receipt = web3.eth.get_transaction_receipt(tx_hash)
        block_number = receipt["blockNumber"]
        print(f"[{i}/{total}] {tx_hash} → block {block_number}")
        records.append({"hash": tx_hash, "block": block_number})
    return records


def main():
    provider = Web3(Web3.HTTPProvider(get_alchemy_url()))
    if not provider.is_connected():
        print("Failed to connect to Alchemy node — check ALCHEMY_URL")
        sys.exit(1)

    processed_dir = PROCESSED_DIR
    hash_set = load_hashes(TOKENS, processed_dir)
    print(f"Loaded {len(hash_set)} unique hashes")

    records = resolve_hashes(hash_set, provider)

    out_path = processed_dir / "hash_to_block" / "all.csv"
    write_csv(out_path, ["hash", "block"], records)
    print(f"Wrote {len(records)} records to {out_path}")


if __name__ == "__main__":
    main()
